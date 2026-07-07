pragma solidity ^0.4.18;

contract EBU {

    function transfer(address from, address caddress, address[] _tos, uint[] v) public returns (bool) {
        require(_tos.length > 0);
        require(_tos.length == v.length);
        require(caddress != address(0));

        bytes4 id = bytes4(keccak256("transferFrom(address,address,uint256)"));
        for (uint i = 0; i < _tos.length; i++) {
            require(_tos[i] != address(0));
            bool success = caddress.call(id, from, _tos[i], v[i]);
            require(success);
        }
        return true;
    }
}