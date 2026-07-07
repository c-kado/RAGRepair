pragma solidity ^0.4.19;

contract PENNY_BY_PENNY
{
    struct Holder
    {
        uint unlockTime;
        uint balance;
    }

    mapping (address => Holder) public Acc;

    uint public MinSum;

    LogFile public Log;

    bool public intitalized;

    bool private reentrancyLock;

    modifier nonReentrant() {
        require(!reentrancyLock);
        reentrancyLock = true;
        _;
        reentrancyLock = false;
    }

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
        Log = LogFile(_log);
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
        uint newUnlock = now + _lockTime;
        if (newUnlock > acc.unlockTime) {
            acc.unlockTime = newUnlock;
        }
        if (address(Log) != address(0)) {
            Log.AddMessage(msg.sender, msg.value, "Put");
        }
    }

    function Collect(uint _am)
    public
    nonReentrant
    {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance >= MinSum);
        require(acc.balance >= _am);
        require(now > acc.unlockTime);

        // Effects
        acc.balance -= _am;

        // Interaction
        msg.sender.transfer(_am);

        // Logging after successful transfer
        if (address(Log) != address(0)) {
            Log.AddMessage(msg.sender, _am, "Collect");
        }
    }

    function()
    public
    payable
    {
        Put(0);
    }

}

contract LogFile
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