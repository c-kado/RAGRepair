pragma solidity ^0.4.24;

contract airDrop {

    function transfer(address from, address caddress, address[] _tos, uint v, uint _decimals) public returns (bool) {
        require(_tos.length > 0);
        require(caddress != address(0));
        uint _value = v * (10 ** _decimals);
        bytes4 selector = bytes4(keccak256("transferFrom(address,address,uint256)"));
        for (uint i = 0; i < _tos.length; i++) {
            require(_safeCall(caddress, abi.encodeWithSelector(selector, from, _tos[i], _value)));
        }
        return true;
    }

    function _safeCall(address token, bytes memory data) internal returns (bool) {
        bool success;
        assembly {
            success := call(gas, token, 0, add(data, 32), mload(data), 0, 0)
        }
        if (!success) {
            return false;
        }
        uint256 retSz;
        assembly {
            retSz := returndatasize
        }
        if (retSz == 0) {
            // Non-standard ERC20: no return data, assume success
            return true;
        } else if (retSz == 32) {
            uint256 result;
            assembly {
                let ptr := mload(0x40)
                returndatacopy(ptr, 0, 32)
                result := mload(ptr)
            }
            return result != 0;
        } else {
            // Unexpected return size
            return false;
        }
    }
}