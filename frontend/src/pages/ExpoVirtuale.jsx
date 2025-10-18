import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Store, 
  Save, 
  Eye, 
  Upload, 
  Image as ImageIcon, 
  FileText, 
  Plus,
  Trash2,
  Edit,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export default function ExpoVirtuale() {
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  
  const [expoPage, setExpoPage] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('info');

  // Form data
  const [formData, setFormData] = useState({
    title: '',
    subtitle: '',
    description: '',
    theme_color: '#0066CC',
    is_published: false
  });

  // Product form
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    category: '',
    price: '',
    currency: 'EUR'
  });
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    loadExpoPage();
    loadProducts();
  }, []);

  const loadExpoPage = async () => {
    try {
      const response = await fetch(`${API_URL}/expo/pages/my/page`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setExpoPage(data);
        setFormData({
          title: data.title || '',
          subtitle: data.subtitle || '',
          description: data.description || '',
          theme_color: data.theme_color || '#0066CC',
          is_published: data.is_published || false
        });
      }
    } catch (error) {
      console.error('Errore nel caricamento della pagina Expo:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/expo/products`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProducts(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei prodotti:', error);
    }
  };

  const handleSaveExpoPage = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${API_URL}/expo/pages/my/page`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        setExpoPage(data);
        setMessage({ type: 'success', text: 'Pagina Expo salvata con successo!' });
      } else {
        setMessage({ type: 'error', text: 'Errore nel salvataggio della pagina' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore di connessione' });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveProduct = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const url = editingProduct 
        ? `${API_URL}/expo/products/${editingProduct.id}`
        : `${API_URL}/expo/products`;
      
      const method = editingProduct ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...productForm,
          price: productForm.price ? parseFloat(productForm.price) : null
        })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Prodotto salvato con successo!' });
        setProductForm({ name: '', description: '', category: '', price: '', currency: 'EUR' });
        setEditingProduct(null);
        loadProducts();
      } else {
        setMessage({ type: 'error', text: 'Errore nel salvataggio del prodotto' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore di connessione' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!confirm('Sei sicuro di voler eliminare questo prodotto?')) return;

    try {
      const response = await fetch(`${API_URL}/expo/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Prodotto eliminato' });
        loadProducts();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore nell\'eliminazione' });
    }
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      description: product.description || '',
      category: product.category || '',
      price: product.price?.toString() || '',
      currency: product.currency || 'EUR'
    });
    setActiveTab('products');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Store className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">Expo Virtuale</h1>
        </div>
        <p className="text-gray-600">
          Gestisci la tua vetrina digitale e il catalogo prodotti
        </p>
      </div>

      {/* Messages */}
      {message.text && (
        <Alert className={`mb-6 ${message.type === 'success' ? 'bg-green-50 text-green-900 border-green-200' : 'bg-red-50 text-red-900 border-red-200'}`}>
          {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Visualizzazioni</p>
                <p className="text-2xl font-bold">{expoPage?.views_count || 0}</p>
              </div>
              <Eye className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Prodotti</p>
                <p className="text-2xl font-bold">{products.length}</p>
              </div>
              <Store className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Stato</p>
                <p className="text-2xl font-bold">{expoPage?.is_published ? 'Pubblicato' : 'Bozza'}</p>
              </div>
              <div className={`w-3 h-3 rounded-full ${expoPage?.is_published ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="info">Informazioni</TabsTrigger>
          <TabsTrigger value="products">Prodotti</TabsTrigger>
          <TabsTrigger value="media">Media & Documenti</TabsTrigger>
        </TabsList>

        {/* Tab Informazioni */}
        <TabsContent value="info">
          <Card>
            <CardHeader>
              <CardTitle>Informazioni Pagina Expo</CardTitle>
              <CardDescription>
                Personalizza la tua vetrina digitale
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Titolo</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Nome della tua azienda"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="subtitle">Sottotitolo</Label>
                <Input
                  id="subtitle"
                  value={formData.subtitle}
                  onChange={(e) => setFormData({ ...formData, subtitle: e.target.value })}
                  placeholder="Slogan o descrizione breve"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descrizione</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Descrizione completa della tua azienda..."
                  rows={6}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="theme_color">Colore Tema</Label>
                  <div className="flex gap-2">
                    <Input
                      id="theme_color"
                      type="color"
                      value={formData.theme_color}
                      onChange={(e) => setFormData({ ...formData, theme_color: e.target.value })}
                      className="w-20 h-10"
                    />
                    <Input
                      value={formData.theme_color}
                      onChange={(e) => setFormData({ ...formData, theme_color: e.target.value })}
                      placeholder="#0066CC"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Stato Pubblicazione</Label>
                  <div className="flex items-center gap-2 h-10">
                    <input
                      type="checkbox"
                      id="is_published"
                      checked={formData.is_published}
                      onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="is_published" className="cursor-pointer">
                      Pubblica la pagina
                    </Label>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button onClick={handleSaveExpoPage} disabled={saving}>
                  <Save className="mr-2 h-4 w-4" />
                  {saving ? 'Salvataggio...' : 'Salva Modifiche'}
                </Button>
                <Button variant="outline">
                  <Eye className="mr-2 h-4 w-4" />
                  Anteprima
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Prodotti */}
        <TabsContent value="products">
          <div className="space-y-6">
            {/* Form Prodotto */}
            <Card>
              <CardHeader>
                <CardTitle>{editingProduct ? 'Modifica Prodotto' : 'Aggiungi Prodotto'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="product_name">Nome Prodotto *</Label>
                  <Input
                    id="product_name"
                    value={productForm.name}
                    onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                    placeholder="Nome del prodotto"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="product_description">Descrizione</Label>
                  <Textarea
                    id="product_description"
                    value={productForm.description}
                    onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                    placeholder="Descrizione del prodotto..."
                    rows={4}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Categoria</Label>
                    <Input
                      id="category"
                      value={productForm.category}
                      onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                      placeholder="es. Macchinari"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="price">Prezzo</Label>
                    <Input
                      id="price"
                      type="number"
                      value={productForm.price}
                      onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                      placeholder="0.00"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="currency">Valuta</Label>
                    <Input
                      id="currency"
                      value={productForm.currency}
                      onChange={(e) => setProductForm({ ...productForm, currency: e.target.value })}
                      placeholder="EUR"
                      maxLength={3}
                    />
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button onClick={handleSaveProduct} disabled={saving || !productForm.name}>
                    <Save className="mr-2 h-4 w-4" />
                    {editingProduct ? 'Aggiorna' : 'Aggiungi'} Prodotto
                  </Button>
                  {editingProduct && (
                    <Button 
                      variant="outline" 
                      onClick={() => {
                        setEditingProduct(null);
                        setProductForm({ name: '', description: '', category: '', price: '', currency: 'EUR' });
                      }}
                    >
                      Annulla
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Lista Prodotti */}
            <Card>
              <CardHeader>
                <CardTitle>I Tuoi Prodotti ({products.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {products.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Store className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Nessun prodotto ancora. Aggiungi il tuo primo prodotto!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {products.map((product) => (
                      <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <h3 className="font-semibold">{product.name}</h3>
                          <p className="text-sm text-gray-600">{product.category}</p>
                          {product.price && (
                            <p className="text-sm font-medium text-primary mt-1">
                              {product.price} {product.currency}
                            </p>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleEditProduct(product)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDeleteProduct(product.id)}>
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab Media */}
        <TabsContent value="media">
          <Card>
            <CardHeader>
              <CardTitle>Media e Documenti</CardTitle>
              <CardDescription>
                Carica immagini, video e documenti per la tua pagina Expo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-gray-500">
                <Upload className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p className="mb-4">Funzionalità di upload in arrivo</p>
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" />
                  Carica File
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

