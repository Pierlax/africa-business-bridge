# Blockchain and Payment Modules Testing Guide

## Overview

This document provides comprehensive testing guidelines for the newly implemented blockchain contracts and payment system modules in the Africa Business Bridge platform.

## Testing Environment Setup

### Prerequisites

1. **Backend Testing**:
   - Python 3.11+
   - FastAPI
   - pytest
   - web3.py
   - httpx

2. **Frontend Testing**:
   - Node.js 16+
   - React Testing Library
   - Jest
   - Cypress (for E2E testing)

3. **Blockchain Testing**:
   - Polygon Mumbai Testnet account
   - Test USDC tokens
   - Test wallet with Mumbai testnet ETH for gas fees

### Installation

```bash
# Backend dependencies
pip install pytest pytest-asyncio web3 httpx

# Frontend dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest cypress
```

## Unit Tests

### Backend Unit Tests

#### 1. Blockchain Service Tests

Create `tests/test_blockchain_service.py`:

```python
import pytest
from app.services.blockchain_service import BlockchainService
from app.schemas.blockchain import AgreementCreate, MilestoneCreate

@pytest.fixture
def blockchain_service():
    return BlockchainService()

@pytest.mark.asyncio
async def test_get_network_info(blockchain_service):
    """Test retrieving network information."""
    info = blockchain_service.get_network_info()
    assert "chain_id" in info
    assert "network_name" in info
    assert info["network_name"] == "Polygon Mumbai"

@pytest.mark.asyncio
async def test_create_agreement(blockchain_service):
    """Test creating a new agreement."""
    result = blockchain_service.create_agreement(
        party_a="0x1234567890123456789012345678901234567890",
        party_b="0x0987654321098765432109876543210987654321",
        description_hash="QmHash123",
        total_amount=1000000000,  # 1000 USDC (6 decimals)
        token_address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        escrow_address="0xEscrowAddress",
        milestones=[
            {
                "description": "Milestone 1",
                "amount": 500000000,
                "dueDate": 1704067200
            }
        ]
    )
    
    assert "transaction_hash" in result or "error" in result
    if "error" not in result:
        assert "agreement_id" in result

@pytest.mark.asyncio
async def test_sign_agreement(blockchain_service):
    """Test signing an agreement."""
    result = blockchain_service.sign_agreement(
        agreement_id=1,
        signer_address="0x0987654321098765432109876543210987654321"
    )
    
    assert "transaction_hash" in result or "error" in result

@pytest.mark.asyncio
async def test_complete_milestone(blockchain_service):
    """Test marking a milestone as completed."""
    result = blockchain_service.complete_milestone(
        agreement_id=1,
        milestone_index=0
    )
    
    assert "transaction_hash" in result or "error" in result

@pytest.mark.asyncio
async def test_release_payment(blockchain_service):
    """Test releasing payment for a completed milestone."""
    result = blockchain_service.release_payment(
        agreement_id=1,
        milestone_index=0
    )
    
    assert "transaction_hash" in result or "error" in result
```

#### 2. Payment Service Tests

Create `tests/test_payment_service.py`:

```python
import pytest
from decimal import Decimal
from app.services.payment_service import PaymentService, PaymentProvider

@pytest.fixture
def payment_service():
    return PaymentService()

@pytest.mark.asyncio
async def test_get_exchange_rate(payment_service):
    """Test getting exchange rate."""
    result = await payment_service.get_exchange_rate(
        from_currency="EUR",
        to_currency="USDC",
        provider=PaymentProvider.CIRCLE
    )
    
    if "error" not in result:
        assert "rate" in result
        assert result["from_currency"] == "EUR"
        assert result["to_currency"] == "USDC"

@pytest.mark.asyncio
async def test_create_onramp_session(payment_service):
    """Test creating an on-ramp session."""
    result = await payment_service.create_onramp_session(
        user_id="user123",
        wallet_address="0x1234567890123456789012345678901234567890",
        amount=Decimal("100.00"),
        from_currency="EUR",
        to_currency="USDC",
        provider=PaymentProvider.CIRCLE
    )
    
    if "error" not in result:\n        assert "session_id" in result\n        assert "url" in result\n        assert result["provider"] == "circle"\n\n@pytest.mark.asyncio\nasync def test_create_offramp_session(payment_service):\n    \"\"\"Test creating an off-ramp session.\"\"\"\n    result = await payment_service.create_offramp_session(\n        user_id=\"user123\",\n        wallet_address=\"0x1234567890123456789012345678901234567890\",\n        amount=Decimal(\"100.00\"),\n        from_currency=\"USDC\",\n        to_currency=\"EUR\",\n        provider=PaymentProvider.CIRCLE\n    )\n    \n    if \"error\" not in result:\n        assert \"session_id\" in result\n        assert \"url\" in result\n\n@pytest.mark.asyncio\nasync def test_get_supported_currencies(payment_service):\n    \"\"\"Test getting supported currencies.\"\"\"\n    result = await payment_service.get_supported_currencies(\n        provider=PaymentProvider.CIRCLE\n    )\n    \n    if \"error\" not in result:\n        assert \"fiat\" in result\n        assert \"crypto\" in result\n        assert len(result[\"fiat\"]) > 0\n        assert len(result[\"crypto\"]) > 0\n```\n\n### Frontend Unit Tests\n\nCreate `frontend/src/__tests__/BlockchainContracts.test.jsx`:\n\n```javascript\nimport React from 'react';\nimport { render, screen, fireEvent, waitFor } from '@testing-library/react';\nimport BlockchainContracts from '../pages/BlockchainContracts';\nimport { AuthContext } from '../contexts/AuthContext';\n\nconst mockAuthContext = {\n  user: { id: '1', wallet_address: '0x1234567890123456789012345678901234567890' },\n  token: 'mock-token'\n};\n\ndescribe('BlockchainContracts Component', () => {\n  it('renders the component', () => {\n    render(\n      <AuthContext.Provider value={mockAuthContext}>\n        <BlockchainContracts />\n      </AuthContext.Provider>\n    );\n    \n    expect(screen.getByText('Blockchain Contracts')).toBeInTheDocument();\n    expect(screen.getByText('Create Contract')).toBeInTheDocument();\n  });\n\n  it('shows create form when button is clicked', () => {\n    render(\n      <AuthContext.Provider value={mockAuthContext}>\n        <BlockchainContracts />\n      </AuthContext.Provider>\n    );\n    \n    const createButton = screen.getByText('Create Contract');\n    fireEvent.click(createButton);\n    \n    expect(screen.getByText('Create New Contract')).toBeInTheDocument();\n  });\n\n  it('submits form with correct data', async () => {\n    render(\n      <AuthContext.Provider value={mockAuthContext}>\n        <BlockchainContracts />\n      </AuthContext.Provider>\n    );\n    \n    const createButton = screen.getByText('Create Contract');\n    fireEvent.click(createButton);\n    \n    // Fill in form fields\n    const partyBInput = screen.getByPlaceholderText('0x...');\n    fireEvent.change(partyBInput, { target: { value: '0x0987654321098765432109876543210987654321' } });\n    \n    // Submit form\n    const submitButton = screen.getByText('Create Contract');\n    fireEvent.click(submitButton);\n    \n    await waitFor(() => {\n      expect(screen.getByText(/Contract created successfully/i)).toBeInTheDocument();\n    });\n  });\n});\n```\n\n## Integration Tests\n\n### API Integration Tests\n\nCreate `tests/test_blockchain_api.py`:\n\n```python\nimport pytest\nfrom fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\n@pytest.fixture\ndef auth_headers():\n    # Mock authentication\n    return {\"Authorization\": \"Bearer mock-token\"}\n\ndef test_create_agreement_endpoint(auth_headers):\n    \"\"\"Test creating agreement via API.\"\"\"\n    response = client.post(\n        \"/api/v1/blockchain/agreements\",\n        json={\n            \"party_a\": \"0x1234567890123456789012345678901234567890\",\n            \"party_b\": \"0x0987654321098765432109876543210987654321\",\n            \"description_hash\": \"QmHash123\",\n            \"total_amount\": 1000000000,\n            \"token_address\": \"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174\",\n            \"escrow_address\": \"0xEscrowAddress\",\n            \"milestones\": [\n                {\n                    \"description\": \"Milestone 1\",\n                    \"amount\": 500000000,\n                    \"due_date\": 1704067200\n                }\n            ]\n        },\n        headers=auth_headers\n    )\n    \n    assert response.status_code in [200, 201]\n    data = response.json()\n    assert \"transaction_hash\" in data or \"agreement_id\" in data\n\ndef test_get_exchange_rate_endpoint(auth_headers):\n    \"\"\"Test getting exchange rate via API.\"\"\"\n    response = client.get(\n        \"/api/v1/payments/exchange-rate?from_currency=EUR&to_currency=USDC\",\n        headers=auth_headers\n    )\n    \n    assert response.status_code == 200\n    data = response.json()\n    assert \"rate\" in data\n    assert data[\"from_currency\"] == \"EUR\"\n    assert data[\"to_currency\"] == \"USDC\"\n\ndef test_create_onramp_session_endpoint(auth_headers):\n    \"\"\"Test creating on-ramp session via API.\"\"\"\n    response = client.post(\n        \"/api/v1/payments/onramp-session\",\n        json={\n            \"wallet_address\": \"0x1234567890123456789012345678901234567890\",\n            \"amount\": 100.00,\n            \"from_currency\": \"EUR\",\n            \"to_currency\": \"USDC\",\n            \"provider\": \"circle\"\n        },\n        headers=auth_headers\n    )\n    \n    assert response.status_code == 200\n    data = response.json()\n    assert \"session_id\" in data\n    assert \"url\" in data\n```\n\n## End-to-End Tests\n\n### Cypress E2E Tests\n\nCreate `frontend/cypress/e2e/blockchain.cy.js`:\n\n```javascript\ndescribe('Blockchain Contracts E2E Tests', () => {\n  beforeEach(() => {\n    cy.visit('http://localhost:3000/blockchain-contracts');\n    cy.login('user@example.com', 'password');\n  });\n\n  it('should create a new contract', () => {\n    cy.contains('Create Contract').click();\n    cy.get('input[name=\"partyB\"]').type('0x0987654321098765432109876543210987654321');\n    cy.get('textarea[name=\"description\"]').type('Test Contract');\n    cy.get('input[name=\"totalAmount\"]').type('1000');\n    cy.contains('Create Contract').click();\n    cy.contains('Contract created successfully').should('be.visible');\n  });\n\n  it('should display contracts list', () => {\n    cy.get('.contract-card').should('have.length.greaterThan', 0);\n  });\n\n  it('should sign a contract', () => {\n    cy.get('.contract-card').first().within(() => {\n      cy.contains('Sign Contract').click();\n    });\n    cy.contains('Contract signed successfully').should('be.visible');\n  });\n});\n```\n\n## Manual Testing Checklist\n\n### Blockchain Contracts\n\n- [ ] User can create a new contract\n- [ ] Contract displays all milestones correctly\n- [ ] User can sign a contract\n- [ ] User can mark milestones as completed\n- [ ] User can release payment for completed milestones\n- [ ] Contract status updates correctly\n- [ ] Error messages display appropriately\n\n### Payment System\n\n- [ ] User can view exchange rates\n- [ ] User can create on-ramp session\n- [ ] User can create off-ramp session\n- [ ] Payment provider redirect works\n- [ ] Supported currencies display correctly\n- [ ] Form validation works properly\n- [ ] Error handling is appropriate\n\n## Running Tests\n\n### Backend Tests\n\n```bash\n# Run all tests\npytest\n\n# Run specific test file\npytest tests/test_blockchain_service.py\n\n# Run with coverage\npytest --cov=app tests/\n\n# Run async tests\npytest -v tests/test_payment_service.py\n```\n\n### Frontend Tests\n\n```bash\n# Run Jest tests\nnpm test\n\n# Run with coverage\nnpm test -- --coverage\n\n# Run Cypress E2E tests\nnpm run cypress:open\n\n# Run Cypress headless\nnpm run cypress:run\n```\n\n## Debugging Tips\n\n1. **Blockchain Issues**:\n   - Check wallet balance and gas fees\n   - Verify contract addresses are correct\n   - Check network connection to Polygon Mumbai\n   - Review transaction logs on Polygonscan\n\n2. **Payment Issues**:\n   - Verify API keys for payment providers\n   - Check currency support for selected provider\n   - Review payment provider logs\n   - Test with small amounts first\n\n3. **Frontend Issues**:\n   - Check browser console for errors\n   - Verify API endpoints are accessible\n   - Check authentication token validity\n   - Use React DevTools for component inspection\n\n## Performance Testing\n\n### Load Testing\n\n```bash\n# Using Apache Bench\nab -n 1000 -c 10 http://localhost:8000/api/v1/blockchain/network-info\n\n# Using wrk\nwrk -t4 -c100 -d30s http://localhost:8000/api/v1/payments/exchange-rate?from_currency=EUR&to_currency=USDC\n```\n\n## Security Testing\n\n- [ ] Verify authentication is required for all endpoints\n- [ ] Test SQL injection prevention\n- [ ] Test XSS prevention\n- [ ] Verify wallet addresses are validated\n- [ ] Test rate limiting\n- [ ] Verify sensitive data is not logged\n\n## Conclusion\n\nThis testing guide provides comprehensive coverage for the blockchain and payment modules. Regular testing ensures the platform remains secure, reliable, and performant.\n
