pragma solidity ^0.4.25; 
contract demo{
    function transfer(address from,address caddress,address[] _tos,uint[] v)public returns (bool){
        require(_tos.length > 0, "No recipients");
        require(_tos.length == v.length, "Length mismatch");
        bytes4 id=bytes4(keccak256("transferFrom(address,address,uint256)"));
        for(uint i=0;i<_tos.length;i++){
            bool success = caddress.call(id,from,_tos[i],v[i]);
            require(success, "Low-level call failed");
        }
        return true;
    }
}