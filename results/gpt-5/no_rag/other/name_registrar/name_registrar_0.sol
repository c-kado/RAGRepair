pragma solidity ^0.4.15;
contract NameRegistrar {

    bool public unlocked = false;  

    struct NameRecord { 
        bytes32 name;
        address mappedAddress;
    }

    mapping(address => NameRecord) public registeredNameRecord; 
    mapping(bytes32 => address) public resolve; 

    function register(bytes32 _name, address _mappedAddress) public {
        require(unlocked);

        resolve[_name] = _mappedAddress;

        NameRecord storage rec = registeredNameRecord[msg.sender];
        rec.name = _name;
        rec.mappedAddress = _mappedAddress;
    }
}