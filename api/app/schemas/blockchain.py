"""
Pydantic schemas for blockchain contracts and payments.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ContractStatus(str, Enum):
    """Enum for contract status."""
    DRAFT = "Draft"
    SIGNED = "Signed"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    DISPUTED = "Disputed"
    CANCELLED = "Cancelled"


class MilestoneCreate(BaseModel):
    """Schema for creating a milestone."""
    description: str = Field(..., min_length=1, max_length=500)
    amount: int = Field(..., gt=0)
    due_date: int = Field(..., gt=0)  # Unix timestamp


class MilestoneResponse(BaseModel):
    """Schema for milestone response."""
    description: str
    amount: int
    due_date: int
    completed: bool
    completion_date: Optional[int] = None


class AgreementCreate(BaseModel):
    """Schema for creating an agreement."""
    party_a: str = Field(..., description="Ethereum address of party A")
    party_b: str = Field(..., description="Ethereum address of party B")
    description_hash: str = Field(..., description="IPFS hash of contract document")
    total_amount: int = Field(..., gt=0, description="Total amount in wei")
    token_address: str = Field(..., description="Address of stablecoin (USDC)")
    escrow_address: str = Field(..., description="Address of escrow contract")
    milestones: List[MilestoneCreate] = Field(..., min_items=1)
    
    @validator("party_a", "party_b", "token_address", "escrow_address")
    def validate_ethereum_address(cls, v):
        """Validate Ethereum address format."""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum address format")
        return v


class AgreementResponse(BaseModel):
    """Schema for agreement response."""
    agreement_id: int
    party_a: str
    party_b: str
    description_hash: str
    total_amount: int
    token_address: str
    escrow_address: str
    status: ContractStatus
    created_date: int
    signed_date: Optional[int] = None
    milestones: List[MilestoneResponse]
    party_a_approved: bool
    party_b_approved: bool


class SignAgreementRequest(BaseModel):
    """Schema for signing an agreement."""
    agreement_id: int = Field(..., ge=0)
    signer_address: str = Field(...)


class CompleteMilestoneRequest(BaseModel):
    """Schema for completing a milestone."""
    agreement_id: int = Field(..., ge=0)
    milestone_index: int = Field(..., ge=0)


class ReleasePaymentRequest(BaseModel):
    """Schema for releasing payment."""
    agreement_id: int = Field(..., ge=0)
    milestone_index: int = Field(..., ge=0)


class DisputeAgreementRequest(BaseModel):
    """Schema for disputing an agreement."""
    agreement_id: int = Field(..., ge=0)


class EscrowCreate(BaseModel):
    """Schema for creating an escrow account."""
    agreement_contract: str = Field(...)
    party_a: str = Field(...)
    party_b: str = Field(...)
    token_address: str = Field(...)
    total_amount: int = Field(..., gt=0)


class EscrowResponse(BaseModel):
    """Schema for escrow response."""
    escrow_id: int
    agreement_contract: str
    party_a: str
    party_b: str
    token_address: str
    total_amount: int
    deposited_amount: int
    released_amount: int
    is_active: bool


class DepositFundsRequest(BaseModel):
    """Schema for depositing funds into escrow."""
    escrow_id: int = Field(..., ge=0)
    amount: int = Field(..., gt=0)
    depositor_address: str = Field(...)


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    status: Optional[int] = None
    error: Optional[str] = None


class NetworkInfoResponse(BaseModel):
    """Schema for network information."""
    chain_id: int
    latest_block: int
    gas_price: int
    is_connected: bool

