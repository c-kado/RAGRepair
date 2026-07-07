pragma solidity ^0.4.19;

contract PRIVATE_ETH_CELL
{
    mapping (address=>uint256) public balances;   

    uint public MinSum;

    LogFile Log;

    bool intitalized;
    bool private locked;

    modifier nonReentrant() {
        require(!locked);
        locked = true;
        _;
        locked = false;
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

    function Deposit()
    public
    payable
    {
        balances[msg.sender]+= msg.value;
        if (address(Log) != address(0)) {
            Log.AddMessage(msg.sender,msg.value,"Put");
        }
    }

    function Collect(uint _am)
    public
    nonReentrant
    {
        require(balances[msg.sender] >= MinSum && balances[msg.sender] >= _am);

        // Effects
        balances[msg.sender] -= _am;

        // Interaction with external account, safe transfer that reverts on failure
        msg.sender.transfer(_am);

        // External logging after state change and while reentrancy lock is held
        if (address(Log) != address(0)) {
            Log.AddMessage(msg.sender,_am,"Collect");
        }
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