"""
Payment Service for managing fiat-to-crypto and crypto-to-fiat conversions.
Integrates with payment gateways like Circle, Transak, or MoonPay.
"""

import os
import httpx
from typing import Dict, Optional
from decimal import Decimal
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class PaymentProvider(str, Enum):
    """Supported payment providers."""
    CIRCLE = "circle"
    TRANSAK = "transak"
    MOONPAY = "moonpay"


class PaymentService:
    """Service for managing payments and currency conversions."""
    
    def __init__(self):
        """Initialize payment service with provider configuration."""
        self.circle_api_key = os.getenv("CIRCLE_API_KEY")
        self.transak_api_key = os.getenv("TRANSAK_API_KEY")
        self.moonpay_api_key = os.getenv("MOONPAY_API_KEY")
        
        self.circle_base_url = "https://api.circle.com/v1"
        self.transak_base_url = "https://api.transak.com"
        self.moonpay_base_url = "https://api.moonpay.com"
        
        self.default_provider = os.getenv("DEFAULT_PAYMENT_PROVIDER", "circle")
    
    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        provider: Optional[PaymentProvider] = None
    ) -> Dict:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code (e.g., 'EUR', 'KES')
            to_currency: Target currency code (e.g., 'USDC', 'USDT')
            provider: Payment provider to use
        
        Returns:
            Exchange rate data or error dict
        """
        provider = provider or self.default_provider
        
        try:
            if provider == PaymentProvider.CIRCLE:
                return await self._get_circle_exchange_rate(from_currency, to_currency)
            elif provider == PaymentProvider.TRANSAK:
                return await self._get_transak_exchange_rate(from_currency, to_currency)
            elif provider == PaymentProvider.MOONPAY:
                return await self._get_moonpay_exchange_rate(from_currency, to_currency)
            else:
                return {"error": f"Unknown provider: {provider}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_circle_exchange_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Get exchange rate from Circle API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.circle_base_url}/prices/convert",
                    params={
                        "from": from_currency,
                        "to": to_currency
                    },
                    headers={"Authorization": f"Bearer {self.circle_api_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": data.get("data", {}).get("rate"),
                        "provider": "circle"
                    }
                else:
                    return {"error": f"Circle API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_transak_exchange_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Get exchange rate from Transak API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.transak_base_url}/api/v1/quotes",
                    params={
                        "fiatCurrency": from_currency,
                        "cryptoCurrency": to_currency,
                        "isBuyOrSell": "BUY",
                        "fiatAmount": "1"
                    },
                    headers={"Authorization": f"Bearer {self.transak_api_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": data.get("data", {}).get("cryptoAmount"),
                        "provider": "transak"
                    }
                else:
                    return {"error": f"Transak API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_moonpay_exchange_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Get exchange rate from MoonPay API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.moonpay_base_url}/v3/currencies/{to_currency}/price",
                    params={"baseCurrency": from_currency},
                    headers={"Authorization": f"Bearer {self.moonpay_api_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": data.get("price"),
                        "provider": "moonpay"
                    }
                else:
                    return {"error": f"MoonPay API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def create_onramp_session(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        provider: Optional[PaymentProvider] = None
    ) -> Dict:
        """
        Create an on-ramp session for fiat-to-crypto conversion.
        
        Args:
            user_id: User ID
            wallet_address: Destination wallet address
            amount: Amount in fiat currency
            from_currency: Source currency (e.g., 'EUR')
            to_currency: Target cryptocurrency (e.g., 'USDC')
            provider: Payment provider to use
        
        Returns:
            On-ramp session data or error dict
        """
        provider = provider or self.default_provider
        
        try:
            if provider == PaymentProvider.CIRCLE:
                return await self._create_circle_onramp(
                    user_id, wallet_address, amount, from_currency, to_currency
                )
            elif provider == PaymentProvider.TRANSAK:
                return await self._create_transak_onramp(
                    user_id, wallet_address, amount, from_currency, to_currency
                )
            elif provider == PaymentProvider.MOONPAY:
                return await self._create_moonpay_onramp(
                    user_id, wallet_address, amount, from_currency, to_currency
                )
            else:
                return {"error": f"Unknown provider: {provider}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_circle_onramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Create on-ramp session with Circle."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.circle_base_url}/onramp/sessions",
                    json={
                        "idempotencyKey": f"{user_id}_{wallet_address}_{amount}",
                        "walletAddress": wallet_address,
                        "amount": str(amount),
                        "sourceCurrency": from_currency,
                        "targetCurrency": to_currency,
                        "chainId": 137  # Polygon
                    },
                    headers={"Authorization": f"Bearer {self.circle_api_key}"}
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "session_id": data.get("data", {}).get("id"),
                        "url": data.get("data", {}).get("url"),
                        "provider": "circle"
                    }
                else:
                    return {"error": f"Circle API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_transak_onramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Create on-ramp session with Transak."""
        try:
            # Transak uses URL parameters for session creation
            params = {
                "apiKey": self.transak_api_key,
                "walletAddress": wallet_address,
                "fiatAmount": str(amount),
                "fiatCurrency": from_currency,
                "cryptoCurrency": to_currency,
                "network": "polygon",
                "isBuyOrSell": "BUY"
            }
            
            url = f"{self.transak_base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            return {
                "session_id": f"{user_id}_{wallet_address}",
                "url": url,
                "provider": "transak"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_moonpay_onramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Create on-ramp session with MoonPay."""
        try:
            # MoonPay uses URL parameters for session creation
            params = {
                "apiKey": self.moonpay_api_key,
                "walletAddress": wallet_address,
                "baseCurrencyAmount": str(amount),
                "baseCurrency": from_currency,
                "cryptoCurrency": to_currency,
                "networkCode": "polygon"
            }
            
            url = f"{self.moonpay_base_url}/buy?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            return {
                "session_id": f"{user_id}_{wallet_address}",
                "url": url,
                "provider": "moonpay"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def create_offramp_session(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        bank_account_id: Optional[str] = None,
        provider: Optional[PaymentProvider] = None
    ) -> Dict:
        """
        Create an off-ramp session for crypto-to-fiat conversion.
        
        Args:
            user_id: User ID
            wallet_address: Source wallet address
            amount: Amount in cryptocurrency
            from_currency: Source cryptocurrency (e.g., 'USDC')
            to_currency: Target currency (e.g., 'EUR')
            bank_account_id: Optional bank account ID for direct transfer
            provider: Payment provider to use
        
        Returns:
            Off-ramp session data or error dict
        """
        provider = provider or self.default_provider
        
        try:
            if provider == PaymentProvider.CIRCLE:
                return await self._create_circle_offramp(
                    user_id, wallet_address, amount, from_currency, to_currency, bank_account_id
                )
            elif provider == PaymentProvider.TRANSAK:
                return await self._create_transak_offramp(
                    user_id, wallet_address, amount, from_currency, to_currency
                )
            elif provider == PaymentProvider.MOONPAY:
                return await self._create_moonpay_offramp(
                    user_id, wallet_address, amount, from_currency, to_currency
                )
            else:
                return {"error": f"Unknown provider: {provider}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_circle_offramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        bank_account_id: Optional[str]
    ) -> Dict:
        """Create off-ramp session with Circle."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.circle_base_url}/offramp/sessions",
                    json={
                        "idempotencyKey": f"{user_id}_{wallet_address}_{amount}",
                        "walletAddress": wallet_address,
                        "amount": str(amount),
                        "sourceCurrency": from_currency,
                        "targetCurrency": to_currency,
                        "bankAccountId": bank_account_id
                    },
                    headers={"Authorization": f"Bearer {self.circle_api_key}"}
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "session_id": data.get("data", {}).get("id"),
                        "url": data.get("data", {}).get("url"),
                        "provider": "circle"
                    }
                else:
                    return {"error": f"Circle API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_transak_offramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Create off-ramp session with Transak."""
        try:
            params = {
                "apiKey": self.transak_api_key,
                "walletAddress": wallet_address,
                "cryptoAmount": str(amount),
                "cryptoCurrency": from_currency,
                "fiatCurrency": to_currency,
                "network": "polygon",
                "isBuyOrSell": "SELL"
            }
            
            url = f"{self.transak_base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            return {
                "session_id": f"{user_id}_{wallet_address}",
                "url": url,
                "provider": "transak"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_moonpay_offramp(
        self,
        user_id: str,
        wallet_address: str,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Create off-ramp session with MoonPay."""
        try:
            params = {
                "apiKey": self.moonpay_api_key,
                "walletAddress": wallet_address,
                "cryptoAmount": str(amount),
                "cryptoCurrency": from_currency,
                "baseCurrency": to_currency,
                "networkCode": "polygon"
            }
            
            url = f"{self.moonpay_base_url}/sell?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            return {
                "session_id": f"{user_id}_{wallet_address}",
                "url": url,
                "provider": "moonpay"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_supported_currencies(
        self,
        provider: Optional[PaymentProvider] = None
    ) -> Dict:
        """
        Get list of supported currencies for a provider.
        
        Args:
            provider: Payment provider
        
        Returns:
            List of supported currencies or error dict
        """
        provider = provider or self.default_provider
        
        # This is a simplified version. In production, this would fetch from the provider's API
        supported_currencies = {
            "circle": {
                "fiat": ["EUR", "USD", "GBP", "CAD"],
                "crypto": ["USDC", "USDT"]
            },
            "transak": {
                "fiat": ["EUR", "USD", "GBP", "KES", "ETB", "TZS"],
                "crypto": ["USDC", "USDT", "ETH", "MATIC"]
            },
            "moonpay": {
                "fiat": ["EUR", "USD", "GBP", "KES", "ETB", "TZS"],
                "crypto": ["USDC", "USDT", "ETH", "MATIC"]
            }
        }
        
        return supported_currencies.get(provider, {"error": "Unknown provider"})

