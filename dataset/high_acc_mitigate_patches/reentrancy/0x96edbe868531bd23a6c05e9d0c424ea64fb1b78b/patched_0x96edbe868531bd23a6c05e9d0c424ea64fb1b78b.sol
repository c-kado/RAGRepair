pragma solidity ^0.4.19;

contract PENNY_BY_PENNY {
    struct Holder {
        uint unlockTime;
        uint balance;
    }

    mapping (address => Holder) public Acc;

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

    function Put(uint _lockTime) public payable {
        Holder storage acc = Acc[msg.sender];
        acc.balance += msg.value;
        if (now + _lockTime > acc.unlockTime) {
            acc.unlockTime = now + _lockTime;
        }
        Log.AddMessage(msg.sender, msg.value, "Put");
    }

    function Collect(uint _am) public {
        Holder storage acc = Acc[msg.sender];
        require(acc.balance >= MinSum && acc.balance >= _am && now > acc.unlockTime);

        uint amount = _am;
        acc.balance -= amount;
        if (!msg.sender.call.value(amount)()) {
            revert();
        }
        Log.AddMessage(msg.sender, amount, "Collect");
    }

    function() public payable {
        Put(0);
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