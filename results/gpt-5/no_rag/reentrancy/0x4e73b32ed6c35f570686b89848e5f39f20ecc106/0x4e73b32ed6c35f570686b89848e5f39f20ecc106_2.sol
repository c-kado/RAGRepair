pragma solidity ^0.4.19;

contract PRIVATE_ETH_CELL
{
    mapping (address=>uint256) public balances;   

    uint public MinSum;

    LogFile Log;

    bool intitalized;
    bool private locked;

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

    function Deposit()
    public
    payable
    {
        balances[msg.sender] += msg.value;
        Log.AddMessage(msg.sender, msg.value, "Put");
    }

    function Collect(uint _am)
    public
    payable
    {
        require(!locked);
        require(balances[msg.sender] >= MinSum);
        require(balances[msg.sender] >= _am);

        locked = true;

        // Effects
        balances[msg.sender] -= _am;

        // Interaction - use transfer to prevent reentrancy
        msg.sender.transfer(_am);

        // Log after successful transfer
        Log.AddMessage(msg.sender, _am, "Collect");

        locked = false;
    }

    function() 
    public 
    payable
    {
        Deposit();
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