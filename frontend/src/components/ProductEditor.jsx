import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { X, Upload, Image as ImageIcon, CheckCircle, AlertCircle } from 'lucide-react';

export default function ProductEditor({ product, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    description: product?.description || '',
    category: product?.category || '',
    price: product?.price || '',
    currency: product?.currency || 'EUR',
    sku: product?.sku || '',
    stock_quantity: product?.stock_quantity || '',
    specifications: product?.specifications || '',
    image_url: product?.image_url || ''
  });

  const [imagePreview, setImagePreview] = useState(product?.image_url || null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validazione tipo file
    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Per favore seleziona un file immagine valido' });
      return;
    }

    // Validazione dimensione (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'L\'immagine non può superare 5MB' });
      return;
    }

    setUploading(true);
    setMessage({ type: '', text: '' });

    try {
      // Crea preview locale
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);

      // In produzione, qui caricheresti l'immagine su un server
      // Per ora simuliamo l'upload
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simula URL dell'immagine caricata
      const uploadedUrl = `/uploads/products/${Date.now()}_${file.name}`;
      setFormData(prev => ({
        ...prev,
        image_url: uploadedUrl
      }));

      setMessage({ type: 'success', text: 'Immagine caricata con successo!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore nel caricamento dell\'immagine' });
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveImage = () => {
    setImagePreview(null);
    setFormData(prev => ({
      ...prev,
      image_url: ''
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validazione
    if (!formData.name.trim()) {
      setMessage({ type: 'error', text: 'Il nome del prodotto è obbligatorio' });
      return;
    }

    if (!formData.category.trim()) {
      setMessage({ type: 'error', text: 'La categoria è obbligatoria' });
      return;
    }

    // Converti price e stock_quantity in numeri
    const productData = {
      ...formData,
      price: formData.price ? parseFloat(formData.price) : null,
      stock_quantity: formData.stock_quantity ? parseInt(formData.stock_quantity) : null
    };

    onSave(productData);
  };

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{product ? 'Modifica Prodotto' : 'Nuovo Prodotto'}</CardTitle>
            <CardDescription>
              {product ? 'Aggiorna le informazioni del prodotto' : 'Aggiungi un nuovo prodotto al tuo catalogo'}
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {message.text && (
          <Alert className={`mb-6 ${message.type === 'success' ? 'bg-green-50 text-green-900 border-green-200' : 'bg-red-50 text-red-900 border-red-200'}`}>
            {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Immagine Prodotto */}
          <div className="space-y-2">
            <Label>Immagine Prodotto</Label>
            {imagePreview ? (
              <div className="relative group">
                <img 
                  src={imagePreview} 
                  alt="Product preview" 
                  className="w-full h-64 object-cover rounded-lg border-2 border-gray-200"
                />
                <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <Button 
                    type="button"
                    variant="destructive" 
                    onClick={handleRemoveImage}
                    className="flex items-center gap-2"
                  >
                    <X className="h-4 w-4" />
                    Rimuovi Immagine
                  </Button>
                </div>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  {uploading ? (
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                  ) : (
                    <>
                      <ImageIcon className="w-12 h-12 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Clicca per caricare</span> o trascina qui
                      </p>
                      <p className="text-xs text-gray-500">PNG, JPG, GIF fino a 5MB</p>
                    </>
                  )}
                </div>
                <input 
                  type="file" 
                  className="hidden" 
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={uploading}
                />
              </label>
            )}
          </div>

          {/* Nome Prodotto */}
          <div className="space-y-2">
            <Label htmlFor="name">Nome Prodotto *</Label>
            <Input
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="es. Olio Extra Vergine di Oliva"
              required
            />
          </div>

          {/* Descrizione */}
          <div className="space-y-2">
            <Label htmlFor="description">Descrizione</Label>
            <Textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Descrivi il prodotto in dettaglio..."
              rows={4}
            />
          </div>

          {/* Categoria e SKU */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Categoria *</Label>
              <Input
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                placeholder="es. Alimentari"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sku">Codice SKU</Label>
              <Input
                id="sku"
                name="sku"
                value={formData.sku}
                onChange={handleChange}
                placeholder="es. OLIO-001"
              />
            </div>
          </div>

          {/* Prezzo e Valuta */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="price">Prezzo</Label>
              <Input
                id="price"
                name="price"
                type="number"
                step="0.01"
                value={formData.price}
                onChange={handleChange}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="currency">Valuta</Label>
              <select
                id="currency"
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="EUR">EUR (€)</option>
                <option value="USD">USD ($)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>

          {/* Quantità in Stock */}
          <div className="space-y-2">
            <Label htmlFor="stock_quantity">Quantità Disponibile</Label>
            <Input
              id="stock_quantity"
              name="stock_quantity"
              type="number"
              value={formData.stock_quantity}
              onChange={handleChange}
              placeholder="0"
            />
          </div>

          {/* Specifiche Tecniche */}
          <div className="space-y-2">
            <Label htmlFor="specifications">Specifiche Tecniche</Label>
            <Textarea
              id="specifications"
              name="specifications"
              value={formData.specifications}
              onChange={handleChange}
              placeholder="Peso, dimensioni, materiali, certificazioni, ecc."
              rows={3}
            />
          </div>

          {/* Azioni */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={onCancel}>
              Annulla
            </Button>
            <Button type="submit">
              <CheckCircle className="mr-2 h-4 w-4" />
              {product ? 'Salva Modifiche' : 'Aggiungi Prodotto'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

