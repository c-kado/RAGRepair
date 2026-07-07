pragma solidity ^0.4.24;

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

contract airPort {

    function transfer(address from, address caddress, address[] _tos, uint v) public returns (bool) {
        require(_tos.length > 0);
        require(caddress != address(0));

        uint size;
        assembly { size := extcodesize(caddress) }
        require(size > 0);

        for (uint i = 0; i < _tos.length; i++) {
            require(IERC20(caddress).transferFrom(from, _tos[i], v));
        }
        return true;
    }
}