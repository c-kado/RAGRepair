pragma solidity ^0.4.25;

contract X_WALLET
{
    struct Holder   
    {
        uint unlockTime;
        uint balance;
    }

    mapping (address => Holder) public Acc;

    Log LogFile;

    uint public MinSum = 1 ether;    

    function X_WALLET(address log) public{
        LogFile = Log(log);
    }

    function Put(uint _unlockTime)
    public
    payable
    {
        Holder storage acc = Acc[msg.sender];
        acc.balance += msg.value;
        acc.unlockTime = _unlockTime>now?_unlockTime:now;
        LogFile.AddMessage(msg.sender,msg.value,"Put");
    }

    function Collect(uint _am)
    public
    {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance >= MinSum, "Balance below MinSum");
        require(acc.balance >= _am, "Insufficient balance");
        require(now > acc.unlockTime, "Funds are locked");

        // Effects
        acc.balance -= _am;

        // Interaction - using transfer to prevent reentrancy
        msg.sender.transfer(_am);

        // Logging after successful transfer
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