pragma solidity ^0.4.19;

contract MONEY_BOX
{
    struct Holder
    {
        uint unlockTime;
        uint balance;
    }

    mapping (address => Holder) public Acc;

    uint public MinSum;

    Log LogFile;

    bool intitalized;

    function SetMinSum(uint _val)
    public
    {
        require(!intitalized);
        MinSum = _val;
    }

    function SetLogFile(address _log)
    public
    {
        require(!intitalized);
        LogFile = Log(_log);
    }

    function Initialized()
    public
    {
        intitalized = true;
    }

    function Put(uint _lockTime)
    public
    payable
    {
        Holder storage acc = Acc[msg.sender];
        acc.balance += msg.value;
        if (now + _lockTime > acc.unlockTime) acc.unlockTime = now + _lockTime;
        if (address(LogFile) != address(0)) {
            LogFile.AddMessage(msg.sender, msg.value, "Put");
        }
    }

    function Collect(uint _am)
    public
    {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance >= MinSum);
        require(acc.balance >= _am);
        require(now > acc.unlockTime);

        // Effects
        acc.balance -= _am;

        // Interaction (safe against reentrancy)
        msg.sender.transfer(_am);

        if (address(LogFile) != address(0)) {
            LogFile.AddMessage(msg.sender, _am, "Collect");
        }
    }

    function()
    public
    payable
    {
        Put(0);
    }

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