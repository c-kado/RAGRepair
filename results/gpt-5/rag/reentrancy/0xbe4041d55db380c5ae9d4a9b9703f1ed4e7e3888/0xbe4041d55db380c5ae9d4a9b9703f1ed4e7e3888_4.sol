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
        if(intitalized)throw;
        MinSum = _val;
    }

    function SetLogFile(address _log)
    public
    {
        if(intitalized)throw;
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
        require(acc.balance + msg.value >= acc.balance);
        acc.balance += msg.value;
        uint newUnlock = now + _lockTime;
        if(newUnlock > acc.unlockTime) acc.unlockTime = newUnlock;
        LogFile.AddMessage(msg.sender,msg.value,"Put");
    }

    function Collect(uint _am)
    public
    payable
    {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance >= MinSum);
        require(acc.balance >= _am);
        require(now > acc.unlockTime);

        acc.balance -= _am;

        msg.sender.transfer(_am);

        LogFile.AddMessage(msg.sender,_am,"Collect");
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