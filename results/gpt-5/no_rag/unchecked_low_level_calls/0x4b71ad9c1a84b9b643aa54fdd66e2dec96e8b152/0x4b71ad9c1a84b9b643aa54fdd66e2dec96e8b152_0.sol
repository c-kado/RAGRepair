pragma solidity ^0.4.24;

contract IERC20 {
    function transferFrom(address from, address to, uint256 value) public returns (bool);
}

contract airPort {

    function isContract(address _addr) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(_addr) }
        return size > 0;
    }

    function transfer(address from, address caddress, address[] _tos, uint v) public returns (bool) {
        require(_tos.length > 0);
        require(isContract(caddress));
        IERC20 token = IERC20(caddress);
        for (uint i = 0; i < _tos.length; i++) {
            require(token.transferFrom(from, _tos[i], v));
        }
        return true;
    }
}