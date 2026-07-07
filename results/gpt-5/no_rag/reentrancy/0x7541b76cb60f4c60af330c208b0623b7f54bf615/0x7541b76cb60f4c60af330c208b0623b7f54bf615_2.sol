pragma solidity ^0.4.25;

contract U_BANK
{
    struct Holder   
    {
        uint unlockTime;
        uint balance;
    }

    mapping (address => Holder) public Acc;

    Log LogFile;

    uint public MinSum = 2 ether;    

    bool private locked;

    modifier nonReentrant() {
        require(!locked);
        locked = true;
        _;
        locked = false;
    }

    function U_BANK(address log) public{
        LogFile = Log(log);
    }

    function Put(uint _unlockTime)
    public
    payable
    nonReentrant
    {
        Holder storage acc = Acc[msg.sender];
        acc.balance += msg.value;
        acc.unlockTime = _unlockTime>now?_unlockTime:now;
        LogFile.AddMessage(msg.sender,msg.value,"Put");
    }

    function Collect(uint _am)
    public
    nonReentrant
    {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance>=MinSum);
        require(acc.balance>=_am);
        require(now>acc.unlockTime);

        // Effects
        acc.balance -= _am;

        // Interaction (uses transfer to limit gas and revert on failure)
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