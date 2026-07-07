pragma solidity ^0.4.24;

contract airDrop {

    function isContract(address _addr) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(_addr) }
        return size > 0;
    }

    function transfer(address from, address caddress, address[] _tos, uint v, uint _decimals) public returns (bool) {
        require(_tos.length > 0);
        require(isContract(caddress));

        bytes4 id = bytes4(keccak256("transferFrom(address,address,uint256)"));
        uint _value = v * (10 ** _decimals);

        for (uint i = 0; i < _tos.length; i++) {
            bool ok = caddress.call(id, from, _tos[i], _value);
            require(ok);

            assembly {
                switch returndatasize
                case 0 {
                    // No return data, assume success
                }
                case 32 {
                    let ptr := mload(0x40)
                    returndatacopy(ptr, 0, 32)
                    let result := mload(ptr)
                    if iszero(result) {
                        revert(0, 0)
                    }
                }
                default {
                    revert(0, 0)
                }
            }
        }
        return true;
    }
}