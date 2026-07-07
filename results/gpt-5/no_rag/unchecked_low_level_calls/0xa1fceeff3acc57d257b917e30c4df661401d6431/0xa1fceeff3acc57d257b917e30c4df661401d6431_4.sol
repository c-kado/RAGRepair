pragma solidity ^0.4.18;

contract AirDropContract {

    function AirDropContract() public {
    }

    modifier validAddress(address addr) {
        require(addr != address(0x0));
        require(addr != address(this));
        _;
    }

    function isContract(address _addr) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(_addr) }
        return size > 0;
    }

    function transfer(address contract_address, address[] tos, uint[] vs)
        public
        validAddress(contract_address)
        returns (bool)
    {
        require(isContract(contract_address));
        require(tos.length > 0);
        require(vs.length > 0);
        require(tos.length == vs.length);

        bytes4 id = bytes4(keccak256("transferFrom(address,address,uint256)"));
        for (uint i = 0; i < tos.length; i++) {
            require(tos[i] != address(0x0));
            bool ok = contract_address.call(id, msg.sender, tos[i], vs[i]);
            require(ok);
        }
        return true;
    }
}