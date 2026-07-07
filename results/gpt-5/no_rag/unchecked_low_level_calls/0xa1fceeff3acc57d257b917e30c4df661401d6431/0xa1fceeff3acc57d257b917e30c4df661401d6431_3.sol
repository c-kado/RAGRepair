pragma solidity ^0.4.18;

contract ERC20 {
    function transferFrom(address from, address to, uint256 value) public returns (bool);
}

contract AirDropContract{

    function AirDropContract() public {
    }

    modifier validAddress( address addr ) {
        require(addr != address(0x0));
        require(addr != address(this));
        _;
    }

    function transfer(address contract_address,address[] tos,uint[] vs)
        public 
        validAddress(contract_address)
        returns (bool){

        require(tos.length > 0);
        require(vs.length > 0);
        require(tos.length == vs.length);

        ERC20 token = ERC20(contract_address);

        for(uint i = 0 ; i < tos.length; i++){
            require(tos[i] != address(0x0));
            require(token.transferFrom(msg.sender, tos[i], vs[i]));
        }
        return true;
    }
}