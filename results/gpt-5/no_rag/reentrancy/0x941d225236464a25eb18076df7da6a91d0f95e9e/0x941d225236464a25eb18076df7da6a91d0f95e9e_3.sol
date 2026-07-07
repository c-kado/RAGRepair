pragma solidity ^0.4.19;

contract ETH_FUND
{
    mapping (address => uint) public balances;

    uint public MinDeposit = 1 ether;

    Log TransferLog;

    uint lastBlock;

    bool private locked;
    modifier nonReentrant() {
        require(!locked);
        locked = true;
        _;
        locked = false;
    }

    function ETH_FUND(address _log)
    public 
    {
        TransferLog = Log(_log);
    }

    function Deposit()
    public
    payable
    nonReentrant
    {
        if(msg.value > MinDeposit)
        {
            balances[msg.sender] += msg.value;
            lastBlock = block.number; // update state before any external call
            TransferLog.AddMessage(msg.sender, msg.value, "Deposit");
        }
    }

    function CashOut(uint _am)
    public
    nonReentrant
    {
        require(_am <= balances[msg.sender] && block.number > lastBlock);

        // Effects
        balances[msg.sender] -= _am;

        // Interaction using transfer to limit gas and prevent reentrancy via fallback
        msg.sender.transfer(_am);

        // External log call after state update and transfer
        TransferLog.AddMessage(msg.sender, _am, "CashOut");
    }

    function() public payable{}    

}

contract Log 
{

    struct Message
    {
        address Sender;
        string  Data;
        uint Val;
        uint  Time;
    }

    Message[] public History;

    Message LastMsg;

    function AddMessage(address _adr,uint _val,string _data)
    public
    {
        LastMsg.Sender = _adr;
        LastMsg.Time = now;
        LastMsg.Val = _val;
        LastMsg.Data = _data;
        History.push(LastMsg);
    }
}