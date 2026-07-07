pragma solidity ^0.4.24;

contract airDrop {

    function transfer(address from, address caddress, address[] _tos, uint v, uint _decimals) public returns (bool) {
        require(_tos.length > 0);
        require(from != address(0));
        require(isContract(caddress));

        bytes4 id = bytes4(keccak256("transferFrom(address,address,uint256)"));
        uint _value = v * 10 ** _decimals;

        for (uint i = 0; i < _tos.length; i++) {
            require(caddress.call(id, from, _tos[i], _value));
        }
        return true;
    }

    function isContract(address _addr) internal view returns (bool) {
        uint size;
        assembly { size := extcodesize(_addr) }
        return size > 0;
    }
}