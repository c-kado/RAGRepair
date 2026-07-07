pragma solidity ^0.4.19;

contract PrivateBank
{
    mapping (address => uint) public balances;

    uint public MinDeposit = 1 ether;

    Log TransferLog;

    bool private locked;

    function PrivateBank(address _lib) public
    {
        TransferLog = Log(_lib);
    }

    modifier noReentrant() {
        require(!locked);
        locked = true;
        _;
        locked = false;
    }

    function Deposit()
    public
    payable
    {
        require(msg.value >= MinDeposit);
        balances[msg.sender] += msg.value;
        TransferLog.AddMessage(msg.sender, msg.value, "Deposit");
    }

    function CashOut(uint _am) public noReentrant
    {
        require(_am > 0 && _am <= balances[msg.sender]);

        // Effects
        balances[msg.sender] -= _am;

        // Interaction - safe transfer that reverts on failure
        msg.sender.transfer(_am);

        // Logging after successful transfer
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