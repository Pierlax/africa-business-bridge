"""
API routes for blockchain contract management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.services.blockchain_service import BlockchainService
from app.schemas.blockchain import (
    AgreementCreate,
    AgreementResponse,
    SignAgreementRequest,
    CompleteMilestoneRequest,
    ReleasePaymentRequest,
    DisputeAgreementRequest,
    EscrowCreate,
    EscrowResponse,
    DepositFundsRequest,
    TransactionResponse,
    NetworkInfoResponse
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/blockchain", tags=["blockchain"])

# Initialize blockchain service
blockchain_service = BlockchainService()


@router.get("/network-info", response_model=NetworkInfoResponse)
async def get_network_info():
    """Get current blockchain network information."""
    info = blockchain_service.get_network_info()
    if "error" in info:
        raise HTTPException(status_code=500, detail=info["error"])
    return info


@router.post("/agreements", response_model=TransactionResponse)
async def create_agreement(
    agreement: AgreementCreate,
    current_user = Depends(get_current_user)
):
    """
    Create a new agreement on blockchain.
    
    Requires authentication.
    """
    result = blockchain_service.create_agreement(
        party_a=agreement.party_a,
        party_b=agreement.party_b,
        description_hash=agreement.description_hash,
        total_amount=agreement.total_amount,
        token_address=agreement.token_address,
        escrow_address=agreement.escrow_address,
        milestones=[
            {
                "description": m.description,
                "amount": m.amount,
                "dueDate": m.due_date
            }
            for m in agreement.milestones
        ]
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/agreements/{agreement_id}/sign", response_model=TransactionResponse)
async def sign_agreement(
    agreement_id: int,
    request: SignAgreementRequest,
    current_user = Depends(get_current_user)
):
    """
    Sign an agreement.
    
    Requires authentication.
    """
    result = blockchain_service.sign_agreement(
        agreement_id=agreement_id,
        signer_address=request.signer_address
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/agreements/{agreement_id}/milestones/{milestone_index}/complete", 
             response_model=TransactionResponse)
async def complete_milestone(
    agreement_id: int,
    milestone_index: int,
    current_user = Depends(get_current_user)
):
    """
    Mark a milestone as completed.
    
    Requires authentication.
    """
    result = blockchain_service.complete_milestone(
        agreement_id=agreement_id,
        milestone_index=milestone_index
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/agreements/{agreement_id}/milestones/{milestone_index}/release-payment",
             response_model=TransactionResponse)
async def release_payment(
    agreement_id: int,
    milestone_index: int,
    current_user = Depends(get_current_user)
):
    """
    Release payment for a completed milestone.
    
    Requires authentication.
    """
    result = blockchain_service.release_payment(
        agreement_id=agreement_id,
        milestone_index=milestone_index
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/agreements/{agreement_id}", response_model=dict)
async def get_agreement(
    agreement_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get agreement details from blockchain.
    
    Requires authentication.
    """
    result = blockchain_service.get_agreement(agreement_id=agreement_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/escrow", response_model=TransactionResponse)
async def create_escrow(
    escrow: EscrowCreate,
    current_user = Depends(get_current_user)
):
    """
    Create a new escrow account.
    
    Requires authentication.
    """
    # This would typically be called internally when creating an agreement
    # Placeholder for direct escrow creation if needed
    raise HTTPException(status_code=501, detail="Use agreement creation endpoint instead")


@router.post("/escrow/{escrow_id}/deposit", response_model=TransactionResponse)
async def deposit_funds(
    escrow_id: int,
    request: DepositFundsRequest,
    current_user = Depends(get_current_user)
):
    """
    Deposit funds into escrow account.
    
    Requires authentication.
    """
    result = blockchain_service.deposit_funds(
        escrow_id=escrow_id,
        amount=request.amount,
        depositor_address=request.depositor_address
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/escrow/{escrow_id}/balance")
async def get_escrow_balance(
    escrow_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get escrow account balance.
    
    Requires authentication.
    """
    result = blockchain_service.get_escrow_balance(escrow_id=escrow_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/agreements/{agreement_id}/dispute", response_model=TransactionResponse)
async def dispute_agreement(
    agreement_id: int,
    request: DisputeAgreementRequest,
    current_user = Depends(get_current_user)
):
    """
    Dispute an agreement.
    
    Requires authentication.
    """
    # This would need to be implemented in the blockchain service
    raise HTTPException(status_code=501, detail="Dispute resolution coming soon")

