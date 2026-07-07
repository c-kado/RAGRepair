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
        if(intitalized) revert();
        MinSum = _val;
    }

    function SetLogFile(address _log)
    public
    {
        if(intitalized) revert();
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
        if(now + _lockTime > acc.unlockTime) acc.unlockTime = now + _lockTime;
        LogFile.AddMessage(msg.sender,msg.value,"Put");
    }

    function Collect(uint _am)
    public
    payable
    {
        Holder storage acc = Acc[msg.sender];
        if( acc.balance>=MinSum && acc.balance>=_am && now>acc.unlockTime)
        {
            acc.balance -= _am;

            if(msg.sender.call.value(_am)())
            {
                LogFile.AddMessage(msg.sender,_am,"Collect");
            } else {
                revert();
            }
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