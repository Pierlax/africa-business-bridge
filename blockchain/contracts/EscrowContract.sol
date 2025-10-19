// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title EscrowContract
 * @dev Manages escrow funds for business agreements
 */
contract EscrowContract is Ownable, ReentrancyGuard {
    
    struct EscrowAccount {
        address agreementContract;
        address partyA;
        address partyB;
        address tokenAddress;
        uint256 totalAmount;
        uint256 depositedAmount;
        uint256 releasedAmount;
        bool isActive;
    }
    
    mapping(uint256 => EscrowAccount) public escrowAccounts;
    mapping(address => uint256[]) public userEscrows;
    uint256 public escrowCounter;
    
    event EscrowCreated(
        uint256 indexed escrowId,
        address indexed agreementContract,
        address indexed partyA,
        address partyB,
        uint256 totalAmount
    );
    
    event FundsDeposited(uint256 indexed escrowId, uint256 amount);
    event FundsReleased(uint256 indexed escrowId, address indexed recipient, uint256 amount);
    event FundsReturned(uint256 indexed escrowId, address indexed recipient, uint256 amount);
    event EscrowClosed(uint256 indexed escrowId);
    
    /**
     * @dev Creates a new escrow account
     */
    function createEscrow(
        address _agreementContract,
        address _partyA,
        address _partyB,
        address _tokenAddress,
        uint256 _totalAmount
    ) external returns (uint256) {
        require(_partyA != address(0) && _partyB != address(0), "Invalid party addresses");
        require(_totalAmount > 0, "Total amount must be greater than 0");
        
        uint256 escrowId = escrowCounter++;
        EscrowAccount storage escrow = escrowAccounts[escrowId];
        
        escrow.agreementContract = _agreementContract;
        escrow.partyA = _partyA;
        escrow.partyB = _partyB;
        escrow.tokenAddress = _tokenAddress;
        escrow.totalAmount = _totalAmount;
        escrow.depositedAmount = 0;
        escrow.releasedAmount = 0;
        escrow.isActive = true;
        
        userEscrows[_partyA].push(escrowId);
        userEscrows[_partyB].push(escrowId);
        
        emit EscrowCreated(escrowId, _agreementContract, _partyA, _partyB, _totalAmount);
        return escrowId;
    }
    
    /**
     * @dev Deposits funds into the escrow account
     */
    function depositFunds(uint256 _escrowId, uint256 _amount) external nonReentrant {
        EscrowAccount storage escrow = escrowAccounts[_escrowId];
        require(escrow.isActive, "Escrow is not active");
        require(msg.sender == escrow.partyA, "Only partyA can deposit funds");
        require(_amount > 0, "Amount must be greater than 0");
        require(
            escrow.depositedAmount + _amount <= escrow.totalAmount,
            "Deposit exceeds total amount"
        );
        
        IERC20 token = IERC20(escrow.tokenAddress);
        require(
            token.transferFrom(msg.sender, address(this), _amount),
            "Transfer failed"
        );
        
        escrow.depositedAmount += _amount;
        emit FundsDeposited(_escrowId, _amount);
    }
    
    /**
     * @dev Releases funds from escrow to partyB
     */
    function releaseFunds(uint256 _escrowId, uint256 _amount) external nonReentrant onlyOwner {
        EscrowAccount storage escrow = escrowAccounts[_escrowId];
        require(escrow.isActive, "Escrow is not active");
        require(_amount > 0, "Amount must be greater than 0");
        require(
            escrow.releasedAmount + _amount <= escrow.depositedAmount,
            "Insufficient funds in escrow"
        );
        
        IERC20 token = IERC20(escrow.tokenAddress);
        require(
            token.transfer(escrow.partyB, _amount),
            "Transfer failed"
        );
        
        escrow.releasedAmount += _amount;
        emit FundsReleased(_escrowId, escrow.partyB, _amount);
    }
    
    /**
     * @dev Returns funds to partyA in case of dispute or cancellation
     */
    function returnFunds(uint256 _escrowId) external nonReentrant onlyOwner {
        EscrowAccount storage escrow = escrowAccounts[_escrowId];
        require(escrow.isActive, "Escrow is not active");
        
        uint256 remainingAmount = escrow.depositedAmount - escrow.releasedAmount;
        require(remainingAmount > 0, "No funds to return");
        
        IERC20 token = IERC20(escrow.tokenAddress);
        require(
            token.transfer(escrow.partyA, remainingAmount),
            "Transfer failed"
        );
        
        emit FundsReturned(_escrowId, escrow.partyA, remainingAmount);
        escrow.isActive = false;
        emit EscrowClosed(_escrowId);
    }
    
    /**
     * @dev Gets escrow account details
     */
    function getEscrow(uint256 _escrowId) external view returns (EscrowAccount memory) {
        return escrowAccounts[_escrowId];
    }
    
    /**
     * @dev Gets balance of escrow account
     */
    function getEscrowBalance(uint256 _escrowId) external view returns (uint256) {
        EscrowAccount storage escrow = escrowAccounts[_escrowId];
        return escrow.depositedAmount - escrow.releasedAmount;
    }
    
    /**
     * @dev Gets user's escrow accounts
     */
    function getUserEscrows(address _user) external view returns (uint256[] memory) {
        return userEscrows[_user];
    }
    
    /**
     * @dev Gets total number of escrow accounts
     */
    function getTotalEscrows() external view returns (uint256) {
        return escrowCounter;
    }
}

