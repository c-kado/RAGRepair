pragma solidity ^0.4.19;

contract PrivateDeposit
{
    mapping (address => uint) public balances;

    uint public MinDeposit = 1 ether;
    address public owner;

    Log TransferLog;

    modifier onlyOwner() {
        require(tx.origin == owner);
        _;
    }    

    function PrivateDeposit() public
    {
        owner = msg.sender;
        TransferLog = new Log();
    }

    function setLog(address _lib) public onlyOwner
    {
        TransferLog = Log(_lib);
    }    

    function Deposit()
    public
    payable
    {
        if(msg.value >= MinDeposit)
        {
            require(balances[msg.sender] + msg.value >= balances[msg.sender]);
            balances[msg.sender] += msg.value;
            TransferLog.AddMessage(msg.sender,msg.value,"Deposit");
        }
    }

    function CashOut(uint _am) public
    {
        if(_am <= balances[msg.sender])
        {            
            // Effects first
            balances[msg.sender] -= _am;

            // Interaction after state change; revert on failure
            if(msg.sender.call.value(_am)())
            {
                TransferLog.AddMessage(msg.sender,_am,"CashOut");
            } 
            else 
            {
                revert();
            }
        }
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