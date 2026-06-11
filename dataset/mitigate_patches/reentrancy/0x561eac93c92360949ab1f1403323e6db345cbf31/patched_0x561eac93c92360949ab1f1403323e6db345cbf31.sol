pragma solidity ^0.4.19;

contract BANK_SAFE {
    mapping (address => uint256) public balances;
    
    uint public MinSum;
    
    LogFile Log;
    
    bool initialized;
    
    function SetMinSum(uint _val) public {
        require(!initialized);
        MinSum = _val;
    }
    
    function SetLogFile(address _log) public {
        require(!initialized);
        Log = LogFile(_log);
    }
    
    function Initialized() public {
        initialized = true;
    }
    
    function Deposit() public payable {
        balances[msg.sender] += msg.value;
        Log.AddMessage(msg.sender, msg.value, "Put");
    }
    
    function Collect(uint _am) public {
        require(balances[msg.sender] >= MinSum && balances[msg.sender] >= _am);
        
        uint amount = _am;
        balances[msg.sender] -= amount;
        Log.AddMessage(msg.sender, amount, "Collect");
        
        require(msg.sender.call.value(amount)());
    }
    
    function() public payable {
        Deposit();
    }
}

contract LogFile {
    struct Message {
        address Sender;
        string Data;
        uint Val;
        uint Time;
    }
    
    Message[] public History;
    
    function AddMessage(address _adr, uint _val, string _data) public {
        Message memory newMessage;
        newMessage.Sender = _adr;
        newMessage.Time = now;
        newMessage.Val = _val;
        newMessage.Data = _data;
        History.push(newMessage);
    }
}