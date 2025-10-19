// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title AgreementContract
 * @dev Manages business agreements between two parties with milestone-based payments
 */
contract AgreementContract is Ownable, ReentrancyGuard {
    
    enum ContractStatus { Draft, Signed, Active, Completed, Disputed, Cancelled }
    
    struct Milestone {
        string description;
        uint256 amount;
        uint256 dueDate;
        bool completed;
        uint256 completionDate;
    }
    
    struct Agreement {
        address partyA;
        address partyB;
        string descriptionHash; // IPFS hash of the legal contract document
        uint256 totalAmount;
        address tokenAddress; // Address of the stablecoin (e.g., USDC)
        address escrowAddress;
        ContractStatus status;
        uint256 createdDate;
        uint256 signedDate;
        Milestone[] milestones;
        bool partyAApproved;
        bool partyBApproved;
    }
    
    mapping(uint256 => Agreement) public agreements;
    uint256 public agreementCounter;
    
    event AgreementCreated(
        uint256 indexed agreementId,
        address indexed partyA,
        address indexed partyB,
        uint256 totalAmount
    );
    
    event AgreementSigned(uint256 indexed agreementId, address indexed signer);
    event MilestoneCompleted(uint256 indexed agreementId, uint256 milestoneIndex);
    event PaymentReleased(uint256 indexed agreementId, uint256 milestoneIndex, uint256 amount);
    event AgreementCompleted(uint256 indexed agreementId);
    event AgreementDisputed(uint256 indexed agreementId);
    
    /**
     * @dev Creates a new agreement
     */
    function createAgreement(
        address _partyA,
        address _partyB,
        string memory _descriptionHash,
        uint256 _totalAmount,
        address _tokenAddress,
        address _escrowAddress,
        string[] memory _milestoneDescriptions,
        uint256[] memory _milestoneAmounts,
        uint256[] memory _milestoneDueDates
    ) external returns (uint256) {
        require(_partyA != address(0) && _partyB != address(0), "Invalid party addresses");
        require(_totalAmount > 0, "Total amount must be greater than 0");
        require(
            _milestoneDescriptions.length == _milestoneAmounts.length &&
            _milestoneAmounts.length == _milestoneDueDates.length,
            "Milestone arrays must have equal length"
        );
        
        uint256 agreementId = agreementCounter++;
        Agreement storage agreement = agreements[agreementId];
        
        agreement.partyA = _partyA;
        agreement.partyB = _partyB;
        agreement.descriptionHash = _descriptionHash;
        agreement.totalAmount = _totalAmount;
        agreement.tokenAddress = _tokenAddress;
        agreement.escrowAddress = _escrowAddress;
        agreement.status = ContractStatus.Draft;
        agreement.createdDate = block.timestamp;
        agreement.partyAApproved = false;
        agreement.partyBApproved = false;
        
        for (uint256 i = 0; i < _milestoneDescriptions.length; i++) {
            agreement.milestones.push(Milestone({
                description: _milestoneDescriptions[i],
                amount: _milestoneAmounts[i],
                dueDate: _milestoneDueDates[i],
                completed: false,
                completionDate: 0
            }));
        }
        
        emit AgreementCreated(agreementId, _partyA, _partyB, _totalAmount);
        return agreementId;
    }
    
    /**
     * @dev Signs the agreement by one of the parties
     */
    function signAgreement(uint256 _agreementId) external {
        Agreement storage agreement = agreements[_agreementId];
        require(
            msg.sender == agreement.partyA || msg.sender == agreement.partyB,
            "Only parties can sign the agreement"
        );
        require(agreement.status == ContractStatus.Draft, "Agreement must be in Draft status");
        
        if (msg.sender == agreement.partyA) {
            agreement.partyAApproved = true;
        } else {
            agreement.partyBApproved = true;
        }
        
        if (agreement.partyAApproved && agreement.partyBApproved) {
            agreement.status = ContractStatus.Signed;
            agreement.signedDate = block.timestamp;
        }
        
        emit AgreementSigned(_agreementId, msg.sender);
    }
    
    /**
     * @dev Activates the agreement (moves from Signed to Active)
     */
    function activateAgreement(uint256 _agreementId) external {
        Agreement storage agreement = agreements[_agreementId];
        require(agreement.status == ContractStatus.Signed, "Agreement must be in Signed status");
        require(
            msg.sender == agreement.partyA || msg.sender == agreement.partyB || msg.sender == owner(),
            "Unauthorized"
        );
        
        agreement.status = ContractStatus.Active;
    }
    
    /**
     * @dev Marks a milestone as completed
     */
    function completeMilestone(uint256 _agreementId, uint256 _milestoneIndex) external {
        Agreement storage agreement = agreements[_agreementId];
        require(agreement.status == ContractStatus.Active, "Agreement must be Active");
        require(_milestoneIndex < agreement.milestones.length, "Invalid milestone index");
        require(!agreement.milestones[_milestoneIndex].completed, "Milestone already completed");
        require(
            msg.sender == agreement.partyB || msg.sender == owner(),
            "Only partyB or owner can complete milestone"
        );
        
        agreement.milestones[_milestoneIndex].completed = true;
        agreement.milestones[_milestoneIndex].completionDate = block.timestamp;
        
        emit MilestoneCompleted(_agreementId, _milestoneIndex);
    }
    
    /**
     * @dev Releases payment for a completed milestone
     */
    function releasePayment(uint256 _agreementId, uint256 _milestoneIndex) external nonReentrant {
        Agreement storage agreement = agreements[_agreementId];
        require(agreement.status == ContractStatus.Active, "Agreement must be Active");
        require(_milestoneIndex < agreement.milestones.length, "Invalid milestone index");
        require(agreement.milestones[_milestoneIndex].completed, "Milestone must be completed");
        require(
            msg.sender == agreement.partyA || msg.sender == owner(),
            "Only partyA or owner can release payment"
        );
        
        uint256 amount = agreement.milestones[_milestoneIndex].amount;
        
        // Transfer from escrow to partyB
        IERC20 token = IERC20(agreement.tokenAddress);
        require(
            token.transferFrom(agreement.escrowAddress, agreement.partyB, amount),
            "Payment transfer failed"
        );
        
        emit PaymentReleased(_agreementId, _milestoneIndex, amount);
        
        // Check if all milestones are completed
        bool allCompleted = true;
        for (uint256 i = 0; i < agreement.milestones.length; i++) {
            if (!agreement.milestones[i].completed) {
                allCompleted = false;
                break;
            }
        }
        
        if (allCompleted) {
            agreement.status = ContractStatus.Completed;
            emit AgreementCompleted(_agreementId);
        }
    }
    
    /**
     * @dev Disputes the agreement
     */
    function disputeAgreement(uint256 _agreementId) external {
        Agreement storage agreement = agreements[_agreementId];
        require(
            msg.sender == agreement.partyA || msg.sender == agreement.partyB,
            "Only parties can dispute"
        );
        require(agreement.status != ContractStatus.Completed, "Cannot dispute completed agreement");
        
        agreement.status = ContractStatus.Disputed;
        emit AgreementDisputed(_agreementId);
    }
    
    /**
     * @dev Gets agreement details
     */
    function getAgreement(uint256 _agreementId) external view returns (Agreement memory) {
        return agreements[_agreementId];
    }
    
    /**
     * @dev Gets milestone details
     */
    function getMilestone(uint256 _agreementId, uint256 _milestoneIndex) 
        external 
        view 
        returns (Milestone memory) 
    {
        return agreements[_agreementId].milestones[_milestoneIndex];
    }
    
    /**
     * @dev Gets total number of agreements
     */
    function getTotalAgreements() external view returns (uint256) {
        return agreementCounter;
    }
}

