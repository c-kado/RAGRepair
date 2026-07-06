pragma solidity ^0.4.24;

contract Map {
    address public owner;
    uint256[] map;

    constructor() public {
        owner = msg.sender;
    }

    function set(uint256 key, uint256 value) public {
        if (map.length <= key) {
            uint256[] memory newMap = new uint256[](key + 1);
            for (uint256 i = 0; i < map.length; i++) {
                newMap[i] = map[i];
            }
            map = newMap;
        }
        map[key] = value;
    }

    function get(uint256 key) public view returns (uint256) {
        return map[key];
    }

    function withdraw() public {
        require(msg.sender == owner);
        msg.sender.transfer(address(this).balance);
    }
}