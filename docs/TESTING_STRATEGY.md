# Strategia di Test e Debugging per Africa Business Bridge

## Introduzione

Questa sezione delinea una strategia di test completa per la piattaforma Africa Business Bridge, coprendo test unitari, di integrazione e end-to-end. Data la natura del progetto e l'ambiente di sviluppo, verranno forniti esempi di test per le funzionalità chiave, che potranno essere estesi e automatizzati in un ambiente di sviluppo più completo.

## 1. Test Unitari

I test unitari si concentrano sulla verifica di singole unità di codice (funzioni, metodi, classi) in isolamento. Sono rapidi da eseguire e aiutano a identificare i bug precocemente.

### 1.1 Backend (Python/FastAPI)

Per il backend, useremo `pytest` per i test unitari. Ogni endpoint API, ogni funzione di servizio e ogni metodo dei modelli dovrebbe avere i propri test unitari.

**Esempio di Test Unitario per Autenticazione (backend/tests/test_auth.py)**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Setup di un database di test in memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
            "full_name": "Test User",
            "role": "pmi"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "pmi"
    assert "id" in data

def test_login_for_access_token(client: TestClient, db_session):
    # Crea un utente di test
    hashed_password = get_password_hash("TestPass123")
    user = User(email="login@example.com", password=hashed_password, full_name="Login User", role=UserRole.PMI)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client: TestClient, db_session):
    # Crea un utente di test e ottieni un token
    hashed_password = get_password_hash("TestPass123")
    user = User(email="current@example.com", password=hashed_password, full_name="Current User", role=UserRole.PMI)
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "current@example.com",
            "password": "TestPass123"
        }
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["full_name"] == "Current User"
```

### 1.2 Frontend (React)

Per il frontend, si possono usare librerie come `Jest` e `React Testing Library` per testare i componenti React in isolamento. Questi test verificano che i componenti renderizzino correttamente, rispondano agli eventi utente e mostrino i dati come previsto.

**Esempio di Test Unitario per un Componente React (frontend/src/components/__tests__/Login.test.jsx)**

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Login from '../../pages/Login';

// Mock della funzione fetch per simulare le chiamate API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ access_token: 'fake-token', token_type: 'bearer' }),
  })
);

describe('Login Component', () => {
  test('renders login form', () => {
    render(
      <Router>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </Router>
    );
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Accedi/i })).toBeInTheDocument();
  });

  test('shows error message on failed login', async () => {
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Credenziali non valide' }),
      })
    );

    render(
      <Router>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </Router>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'wrong@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongpass' } });
    fireEvent.click(screen.getByRole('button', { name: /Accedi/i }));

    await waitFor(() => {
      expect(screen.getByText(/Credenziali non valide/i)).toBeInTheDocument();
    });
  });

  test('navigates to dashboard on successful login', async () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));

    render(
      <Router>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </Router>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'TestPass123' } });
    fireEvent.click(screen.getByRole('button', { name: /Accedi/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });
});
```

## 2. Test di Integrazione

I test di integrazione verificano che diversi moduli o servizi funzionino correttamente insieme. Per un'applicazione full-stack, questo significa testare l'interazione tra frontend e backend, e tra backend e database.

### 2.1 Backend-Database Integration Tests

Questi test assicurano che le operazioni CRUD (Create, Read, Update, Delete) sui modelli del database funzionino come previsto attraverso le API del backend.

**Esempio di Test di Integrazione per Expo Virtuale (backend/tests/test_expo.py)**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, UserRole, PMIProfile
from app.models.expo import ExpoPage, Product
from app.core.security import get_password_hash

# ... (setup del database di test e client come in test_auth.py)

@pytest.fixture(name="pmi_user_and_token")
def pmi_user_and_token_fixture(db_session, client):
    hashed_password = get_password_hash("TestPass123")
    user = User(email="pmi@test.com", password=hashed_password, full_name="Test PMI", role=UserRole.PMI)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    pmi_profile = PMIProfile(user_id=user.id, company_name="Test Company", sector="IT")
    db_session.add(pmi_profile)
    db_session.commit()
    db_session.refresh(pmi_profile)

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "pmi@test.com",
            "password": "TestPass123"
        }
    )
    token = login_response.json()["access_token"]
    return user, pmi_profile, token

def test_get_my_expo_page(client: TestClient, pmi_user_and_token):
    user, pmi_profile, token = pmi_user_and_token
    response = client.get(
        "/api/v1/expo/pages/my/page",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pmi_id"] == pmi_profile.id
    assert data["title"] == "" # Pagina creata vuota

def test_update_my_expo_page(client: TestClient, pmi_user_and_token):
    user, pmi_profile, token = pmi_user_and_token
    update_data = {"title": "My Awesome Expo", "description": "A great description"}
    response = client.put(
        "/api/v1/expo/pages/my/page",
        json=update_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Awesome Expo"
    assert data["description"] == "A great description"

def test_create_product(client: TestClient, pmi_user_and_token):
    user, pmi_profile, token = pmi_user_and_token
    product_data = {"name": "New Product", "category": "Tech", "price": 100.0}
    response = client.post(
        "/api/v1/expo/products",
        json=product_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"
    assert data["pmi_id"] == pmi_profile.id
```

### 2.2 Frontend-Backend Integration Tests

Questi test verificano che il frontend possa comunicare correttamente con il backend, inviando richieste e gestendo le risposte. Possono essere eseguiti usando strumenti come `Cypress` o `Playwright` per simulare interazioni utente reali e verificare il flusso completo.

**Esempio di Test di Integrazione Frontend (Cypress)**

```javascript
// cypress/e2e/expo_virtuale.cy.js
describe('Expo Virtuale Module', () => {
  beforeEach(() => {
    // Assicurati che l'utente sia loggato prima di ogni test
    cy.login('pmi@test.com', 'TestPass123'); // Funzione di login custom
    cy.visit('/expo');
  });

  it('should display the Expo Virtuale page title', () => {
    cy.contains('h1', 'Expo Virtuale').should('be.visible');
  });

  it('should allow updating expo page information', () => {
    const newTitle = 'Updated Company Name';
    const newDescription = 'This is an updated description for the expo page.';

    cy.get('#title').clear().type(newTitle);
    cy.get('#description').clear().type(newDescription);
    cy.contains('button', 'Salva Modifiche').click();

    cy.contains('Pagina Expo salvata con successo!').should('be.visible');
    cy.get('#title').should('have.value', newTitle);
  });

  it('should allow adding a new product', () => {
    cy.get('button').contains('Prodotti').click(); // Switch to products tab
    cy.get('#product_name').type('Test Product');
    cy.get('#product_description').type('Description for test product');
    cy.get('#category').type('Electronics');
    cy.get('#price').type('99.99');
    cy.get('button').contains('Aggiungi Prodotto').click();

    cy.contains('Prodotto salvato con successo!').should('be.visible');
    cy.contains('h3', 'Test Product').should('be.visible');
  });

  it('should allow deleting a product', () => {
    cy.get('button').contains('Prodotti').click(); // Switch to products tab
    // Assumiamo che ci sia almeno un prodotto da eliminare
    cy.get('h3').contains('Test Product').parents('.flex').find('button').contains('Trash2').click(); // Clicca sull'icona del cestino
    cy.on('window:confirm', () => true); // Accetta la finestra di conferma

    cy.contains('Prodotto eliminato').should('be.visible');
    cy.contains('h3', 'Test Product').should('not.exist');
  });
});
```

## 3. Test End-to-End (E2E)

I test E2E simulano il percorso completo dell'utente attraverso l'applicazione, dal login all'esecuzione di funzionalità complesse che coinvolgono più moduli. Questi test sono cruciali per verificare che l'intera applicazione funzioni come un sistema coeso.

**Esempio di Test E2E per il Flusso di Business Matching (Cypress/Playwright)**

```javascript
// cypress/e2e/business_matching_flow.cy.js
describe('Business Matching End-to-End Flow', () => {
  it('should allow a PMI to register, login, view suggestions, and accept a match', () => {
    // 1. Registrazione PMI
    cy.visit('/register');
    cy.get('#full_name').type('PMI Test User');
    cy.get('#email').type('pmi_e2e@test.com');
    cy.get('#role').select('pmi');
    cy.get('#password').type('SecurePass123');
    cy.get('#confirm_password').type('SecurePass123');
    cy.get('button').contains('Registrati').click();
    cy.url().should('include', '/login');

    // 2. Login PMI
    cy.get('#email').type('pmi_e2e@test.com');
    cy.get('#password').type('SecurePass123');
    cy.get('button').contains('Accedi').click();
    cy.url().should('include', '/dashboard');

    // 3. Naviga alla pagina Partner
    cy.get('a[href="/partners"]').click();
    cy.url().should('include', '/partners');
    cy.contains('h1', 'Partner Locali').should('be.visible');

    // 4. Visualizza suggerimenti e accetta un match (assumendo che ci siano suggerimenti)
    cy.get('button').contains('Suggerimenti IA').click();
    cy.get('.MuiCard-root').first().as('firstMatchCard'); // Seleziona la prima card di match
    cy.get('@firstMatchCard').find('button').contains('Accetta Match').click();

    cy.contains('Match accettato!').should('be.visible');
    cy.get('button').contains('I Miei Match').click();
    cy.get('.MuiCard-root').contains('Match #').should('be.visible'); // Verifica che il match sia nella lista
  });
});
```

## 4. Debugging

Il debugging è il processo di identificazione e risoluzione dei bug. Una buona strategia di debugging include:

*   **Logging**: Utilizzare log dettagliati nel backend e nel frontend per tracciare il flusso dell'applicazione e identificare i punti di errore.
*   **Strumenti di Sviluppo del Browser**: Utilizzare la console del browser, il debugger e gli strumenti di rete per ispezionare il comportamento del frontend e le chiamate API.
*   **Debugger del Backend**: Utilizzare un debugger Python (es. `pdb` o strumenti IDE come VS Code debugger) per eseguire il codice passo dopo passo e ispezionare le variabili.
*   **Monitoraggio delle Eccezioni**: Implementare un sistema di monitoraggio delle eccezioni (es. Sentry) per catturare e segnalare gli errori in produzione.

## 5. Strumenti Consigliati

| Categoria | Strumento | Descrizione |
|-----------|-----------|-------------|
| **Backend Testing** | `pytest` | Framework di test Python per unit e integration tests. |
| **Frontend Testing** | `Jest` | Framework di test JavaScript per unit tests di React. |
| **Frontend Testing** | `React Testing Library` | Utilità per testare i componenti React in modo user-centric. |
| **E2E Testing** | `Cypress` / `Playwright` | Framework per test end-to-end, simulazione interazioni utente. |
| **Code Quality** | `Black`, `isort`, `ESLint`, `Prettier` | Strumenti per formattazione e linting del codice. |
| **API Testing** | `Postman`, `Insomnia` | Strumenti per testare manualmente gli endpoint API. |
| **Database Inspection** | `pgAdmin`, `DBeaver` | Strumenti GUI per visualizzare e gestire il database PostgreSQL. |

## Conclusione

Questa strategia fornisce una base per garantire la qualità e la stabilità della piattaforma Africa Business Bridge. L'implementazione di questi test, insieme a pratiche di debugging efficaci, sarà fondamentale per il successo del progetto. Si raccomanda di integrare questi test in un pipeline CI/CD per automatizzare l'esecuzione e garantire feedback continui sullo stato del codice.

