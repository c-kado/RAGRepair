pragma solidity ^0.4.19;

contract PrivateBank
{
    mapping (address => uint) public balances;

    uint public MinDeposit = 1 ether;

    Log TransferLog;

    bool private reEntrancyMutex;

    function PrivateBank(address _log) public
    {
        TransferLog = Log(_log);
    }

    function Deposit()
    public
    payable
    {
        if(msg.value >= MinDeposit)
        {
            balances[msg.sender] += msg.value;
            TransferLog.AddMessage(msg.sender, msg.value, "Deposit");
        }
    }

    function CashOut(uint _am) public
    {
        require(_am <= balances[msg.sender]);
        require(!reEntrancyMutex);
        reEntrancyMutex = true;

        // Effects
        balances[msg.sender] -= _am;

        // Interaction
        require(msg.sender.call.value(_am)());

        // Logging after successful transfer
        TransferLog.AddMessage(msg.sender, _am, "CashOut");

        reEntrancyMutex = false;
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