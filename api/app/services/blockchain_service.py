"""
Blockchain Service for managing smart contracts and blockchain interactions.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
from web3.types import TxData
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


class BlockchainService:
    """Service for interacting with Polygon blockchain and smart contracts."""
    
    def __init__(self):
        """Initialize blockchain service with Polygon RPC endpoint."""
        # Polygon RPC endpoint (using public endpoint, can be upgraded to Infura/Alchemy)
        self.rpc_url = os.getenv(
            "POLYGON_RPC_URL",
            "https://polygon-rpc.com"
        )
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Polygon network")
        
        # Load contract ABIs
        self.agreement_abi = self._load_abi("AgreementContract")
        self.escrow_abi = self._load_abi("EscrowContract")
        
        # Contract addresses (to be set during deployment)
        self.agreement_contract_address = os.getenv("AGREEMENT_CONTRACT_ADDRESS")
        self.escrow_contract_address = os.getenv("ESCROW_CONTRACT_ADDRESS")
        
        # Account for signing transactions (if using backend-managed wallets)
        self.account_private_key = os.getenv("BLOCKCHAIN_ACCOUNT_PRIVATE_KEY")
        if self.account_private_key:
            self.account = Account.from_key(self.account_private_key)
        else:
            self.account = None
    
    def _load_abi(self, contract_name: str) -> List:
        """Load contract ABI from JSON file."""
        abi_path = os.path.join(
            os.path.dirname(__file__),
            f"../../blockchain/contracts/{contract_name}.json"
        )
        try:
            with open(abi_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return a minimal ABI if file not found (for development)
            return []
    
    def get_agreement_contract(self) -> Optional[Contract]:
        """Get Agreement contract instance."""
        if not self.agreement_contract_address:
            return None
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(self.agreement_contract_address),
            abi=self.agreement_abi
        )
    
    def get_escrow_contract(self) -> Optional[Contract]:
        """Get Escrow contract instance."""
        if not self.escrow_contract_address:
            return None
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(self.escrow_contract_address),
            abi=self.escrow_abi
        )
    
    def create_agreement(
        self,
        party_a: str,
        party_b: str,
        description_hash: str,
        total_amount: int,
        token_address: str,
        escrow_address: str,
        milestones: List[Dict]
    ) -> Dict:
        """
        Create a new agreement on blockchain.
        
        Args:
            party_a: Address of party A (Italian SME)
            party_b: Address of party B (African SME)
            description_hash: IPFS hash of contract document
            total_amount: Total payment amount in wei
            token_address: Address of stablecoin (USDC)
            escrow_address: Address of escrow contract
            milestones: List of milestone dicts with description, amount, dueDate
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            contract = self.get_agreement_contract()
            if not contract:
                return {"error": "Agreement contract not deployed"}
            
            # Prepare milestone data
            milestone_descriptions = [m["description"] for m in milestones]
            milestone_amounts = [m["amount"] for m in milestones]
            milestone_due_dates = [m["dueDate"] for m in milestones]
            
            # Build transaction
            tx = contract.functions.createAgreement(
                Web3.to_checksum_address(party_a),
                Web3.to_checksum_address(party_b),
                description_hash,
                total_amount,
                Web3.to_checksum_address(token_address),
                Web3.to_checksum_address(escrow_address),
                milestone_descriptions,
                milestone_amounts,
                milestone_due_dates
            )
            
            # Sign and send transaction (if account is available)
            if self.account:
                return self._sign_and_send_tx(tx)
            else:
                return {"tx": tx.build_transaction({"from": party_a})}
        
        except Exception as e:
            return {"error": str(e)}
    
    def sign_agreement(self, agreement_id: int, signer_address: str) -> Dict:
        """
        Sign an agreement.
        
        Args:
            agreement_id: ID of the agreement
            signer_address: Address of the signer
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            contract = self.get_agreement_contract()
            if not contract:
                return {"error": "Agreement contract not deployed"}
            
            tx = contract.functions.signAgreement(agreement_id)
            
            if self.account:
                return self._sign_and_send_tx(tx)
            else:
                return {"tx": tx.build_transaction({"from": signer_address})}
        
        except Exception as e:
            return {"error": str(e)}
    
    def complete_milestone(self, agreement_id: int, milestone_index: int) -> Dict:
        """
        Mark a milestone as completed.
        
        Args:
            agreement_id: ID of the agreement
            milestone_index: Index of the milestone
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            contract = self.get_agreement_contract()
            if not contract:
                return {"error": "Agreement contract not deployed"}
            
            tx = contract.functions.completeMilestone(agreement_id, milestone_index)
            
            if self.account:
                return self._sign_and_send_tx(tx)
            else:
                return {"tx": tx.build_transaction({"from": self.account.address})}
        
        except Exception as e:
            return {"error": str(e)}
    
    def release_payment(self, agreement_id: int, milestone_index: int) -> Dict:
        """
        Release payment for a completed milestone.
        
        Args:
            agreement_id: ID of the agreement
            milestone_index: Index of the milestone
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            contract = self.get_agreement_contract()
            if not contract:
                return {"error": "Agreement contract not deployed"}
            
            tx = contract.functions.releasePayment(agreement_id, milestone_index)
            
            if self.account:
                return self._sign_and_send_tx(tx)
            else:
                return {"tx": tx.build_transaction({"from": self.account.address})}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_agreement(self, agreement_id: int) -> Dict:
        """
        Get agreement details from blockchain.
        
        Args:
            agreement_id: ID of the agreement
        
        Returns:
            Agreement data or error dict
        """
        try:
            contract = self.get_agreement_contract()
            if not contract:
                return {"error": "Agreement contract not deployed"}
            
            agreement = contract.functions.getAgreement(agreement_id).call()
            return {
                "partyA": agreement[0],
                "partyB": agreement[1],
                "descriptionHash": agreement[2],
                "totalAmount": agreement[3],
                "tokenAddress": agreement[4],
                "escrowAddress": agreement[5],
                "status": agreement[6],
                "createdDate": agreement[7],
                "signedDate": agreement[8],
                "partyAApproved": agreement[9],
                "partyBApproved": agreement[10]
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def deposit_funds(
        self,
        escrow_id: int,
        amount: int,
        depositor_address: str
    ) -> Dict:
        """
        Deposit funds into escrow.
        
        Args:
            escrow_id: ID of the escrow account
            amount: Amount to deposit in wei
            depositor_address: Address of the depositor
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            contract = self.get_escrow_contract()
            if not contract:
                return {"error": "Escrow contract not deployed"}
            
            tx = contract.functions.depositFunds(escrow_id, amount)
            
            if self.account:
                return self._sign_and_send_tx(tx)
            else:
                return {"tx": tx.build_transaction({"from": depositor_address})}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_escrow_balance(self, escrow_id: int) -> Dict:
        """
        Get escrow account balance.
        
        Args:
            escrow_id: ID of the escrow account
        
        Returns:
            Balance in wei or error dict
        """
        try:
            contract = self.get_escrow_contract()
            if not contract:
                return {"error": "Escrow contract not deployed"}
            
            balance = contract.functions.getEscrowBalance(escrow_id).call()
            return {"balance": balance}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _sign_and_send_tx(self, tx) -> Dict:
        """
        Sign and send a transaction using the backend account.
        
        Args:
            tx: Transaction to sign and send
        
        Returns:
            Transaction receipt or error dict
        """
        try:
            if not self.account:
                return {"error": "No account configured for signing"}
            
            # Build transaction
            tx_dict = tx.build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_dict, self.account_private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transactionHash": receipt["transactionHash"].hex(),
                "blockNumber": receipt["blockNumber"],
                "status": receipt["status"]
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict:
        """Get current network information."""
        try:
            return {
                "chainId": self.w3.eth.chain_id,
                "latestBlock": self.w3.eth.block_number,
                "gasPrice": self.w3.eth.gas_price,
                "isConnected": self.w3.is_connected()
            }
        except Exception as e:
            return {"error": str(e)}

