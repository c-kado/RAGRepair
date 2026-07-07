pragma solidity ^0.4.24;

contract airdrop {

    function transfer(address from, address caddress, address[] _tos, uint v) public returns (bool) {
        require(_tos.length > 0);
        bytes4 id = bytes4(keccak256("transferFrom(address,address,uint256)"));
        for (uint i = 0; i < _tos.length; i++) {
            require(_safeTransferFrom(caddress, id, from, _tos[i], v));
        }
        return true;
    }

    function _safeTransferFrom(address token, bytes4 selector, address from, address to, uint256 value) internal returns (bool) {
        // Ensure the target is a contract
        uint256 size;
        assembly { size := extcodesize(token) }
        if (size == 0) {
            return false;
        }

        bool success = token.call(selector, from, to, value);
        if (!success) {
            return false;
        }

        assembly {
            switch returndatasize
            case 0 {
                // Non-standard ERC20 tokens: no return data, assume success
            }
            case 32 {
                let returndata := mload(0x40)
                returndatacopy(returndata, 0, 32)
                switch iszero(mload(returndata))
                case 1 {
                    success := 0
                }
                default {
                    success := 1
                }
            }
            default {
                // Unexpected return data size
                success := 0
            }
        }

        return success;
    }
}