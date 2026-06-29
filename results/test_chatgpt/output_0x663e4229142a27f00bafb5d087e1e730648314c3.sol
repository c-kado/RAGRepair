```solidity
pragma solidity ^0.4.24;

contract ERC20 {
    function totalSupply() constant returns (uint supply);
    function balanceOf( address who ) constant returns (uint value);
    function allowance( address owner, address spender ) constant returns (uint _allowance);

    function transfer( address to, uint value) returns (bool ok);
    function transferFrom( address from, address to, uint value) returns (bool ok);
    function approve( address spender, uint value ) returns (bool ok);

    event Transfer( address indexed from, address indexed to, uint value);
    event Approval( address indexed owner, address indexed spender, uint value);
}

contract Ownable {
  address public owner;

  function Ownable() {
    owner = msg.sender;
  }

  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  function transferOwnership(address newOwner) onlyOwner {
    if (newOwner != address(0)) {
      owner = newOwner;
    }
  }

}

contract ERC721 {

    function totalSupply() public view returns (uint256 total);
    function balanceOf(address _owner) public view returns (uint256 balance);
    function ownerOf(uint256 _tokenId) external view returns (address owner);
    function approve(address _to, uint256 _tokenId) external;
    function transfer(address _to, uint256 _tokenId) external;
    function transferFrom(address _from, address _to, uint256 _tokenId) external;

    event Transfer(address from, address to, uint256 tokenId);
    event Approval(address owner, address approved, uint256 tokenId);

    function supportsInterface(bytes4 _interfaceID) external view returns (bool);
}

contract GeneScienceInterface {

    function isGeneScience() public pure returns (bool);

    function mixGenes(uint256[2] genes1, uint256[2] genes2,uint256 g1,uint256 g2, uint256 targetBlock) public returns (uint256[2]);

    function getPureFromGene(uint256[2] gene) public view returns(uint256);

    function getSex(uint256[2] gene) public view returns(uint256);

    function getWizzType(uint256[2] gene) public view returns(uint256);

    function clearWizzType(uint256[2] _gene) public returns(uint256[2]);
}

contract PandaAccessControl {

    event ContractUpgrade(address newContract);

    address public ceoAddress;
    address public cfoAddress;
    address public cooAddress;

    bool public paused = false;

    modifier onlyCEO() {
        require(msg.sender == ceoAddress);
        _;
    }

    modifier onlyCFO() {
        require(msg.sender == cfoAddress);
        _;
    }

    modifier onlyCOO() {
        require(msg.sender == cooAddress);
        _;
    }

    modifier onlyCLevel() {
        require(
            msg.sender == cooAddress ||
            msg.sender == ceoAddress ||
            msg.sender == cfoAddress
        );
        _;
    }

    function setCEO(address _newCEO) external onlyCEO {
        require(_newCEO != address(0));

        ceoAddress = _newCEO;
    }

    function setCFO(address _newCFO) external onlyCEO {
        require(_newCFO != address(0));

        cfoAddress = _newCFO;
    }

    function setCOO(address _newCOO) external onlyCEO {
        require(_newCOO != address(0));

        cooAddress = _newCOO;
    }

    modifier whenNotPaused() {
        require(!paused);
        _;
    }

    modifier whenPaused {
        require(paused);
        _;
    }

    function pause() external onlyCLevel whenNotPaused {
        paused = true;
    }

    function unpause() public onlyCEO whenPaused {

        paused = false;
    }
}

contract PandaBase is PandaAccessControl {

    uint256 public constant GEN0_TOTAL_COUNT = 16200;
    uint256 public gen0CreatedCount;

    event Birth(address owner, uint256 pandaId, uint256 matronId, uint256 sireId, uint256[2] genes);

    event Transfer(address from, address to, uint256 tokenId);

    struct Panda {

        uint256[2] genes;

        uint64 birthTime;

        uint64 cooldownEndBlock;

        uint32 matronId;
        uint32 sireId;

        uint32 siringWithId;

        uint16 cooldownIndex;

        uint16 generation;
    }

    uint32[9] public cooldowns = [
        uint32(5 minutes),
        uint32(30 minutes),
        uint32(2 hours),
        uint32(4 hours),
        uint32(8 hours),
        uint32(24 hours),
        uint32(48 hours),
        uint32(72 hours),
        uint32(7 days)
    ];

    uint256 public secondsPerBlock = 15;

    Panda[] pandas;

    mapping (uint256 => address) public pandaIndexToOwner;

    mapping (address => uint256) ownershipTokenCount;

    mapping (uint256 => address) public pandaIndexToApproved;

    mapping (uint256 => address) public sireAllowedToAddress;

    SaleClockAuction public saleAuction;

    SiringClockAuction public siringAuction;

    GeneScienceInterface public geneScience;

    SaleClockAuctionERC20 public saleAuctionERC20;

    mapping (uint256 => uint256) public wizzPandaQuota;
    mapping (uint256 => uint256) public wizzPandaCount;

    function getWizzPandaQuotaOf(uint256 _tp) view external returns(uint256) {
        return wizzPandaQuota[_tp];
    }

    function getWizzPandaCountOf(uint256 _tp) view external returns(uint256) {
        return wizzPandaCount[_tp];
    }

    function setTotalWizzPandaOf(uint256 _tp,uint256 _total) external onlyCLevel {
        require (wizzPandaQuota[_tp]==0);
        require (_total==uint256(uint32(_total)));
        wizzPandaQuota[_tp] = _total;
    }

    function getWizzTypeOf(uint256 _id) view external returns(uint256) {
        Panda memory _p = pandas[_id];
        return geneScience.getWizzType(_p.genes);
    }

    function _transfer(address _from, address _to, uint256 _tokenId) internal {

        ownershipTokenCount[_to]++;

        pandaIndexToOwner[_tokenId] = _to;

        if (_from != address(0)) {
            ownershipTokenCount[_from]--;

            delete sireAllowedToAddress[_tokenId];

            delete pandaIndexToApproved[_tokenId];
        }

        Transfer(_from, _to, _tokenId);
    }

    function _createPanda(
        uint256 _matronId,
        uint256 _sireId,
        uint256 _generation,
        uint256[2] _genes,
        address _owner
    )
        internal
        returns (uint)
    {

        require(_matronId == uint256(uint32(_matronId)));
        require(_sireId == uint256(uint32(_sireId)));
        require(_generation == uint256(uint16(_generation)));

        uint16 cooldownIndex = 0;

        if (pandas.length>0){
            uint16 pureDegree = uint16(geneScience.getPureFromGene(_genes));
            if (pureDegree==0) {
                pureDegree = 1;
            }
            cooldownIndex = 1000/pureDegree;
            if (cooldownIndex%10 < 5){
                cooldownIndex = cooldownIndex/10;
            }else{
                cooldownIndex = cooldownIndex/10 + 1;
            }
            cooldownIndex = cooldownIndex - 1;
            if (cooldownIndex > 8) {
                cooldownIndex = 8;
            }
            uint256 _tp = geneScience.getWizzType(_genes);
            if (_tp>0 && wizzPandaQuota[_tp]<=wizzPandaCount[_tp]) {
                _genes = geneScience.clearWizzType(_genes);
                _tp = 0;
            }

            if (_tp == 1){
                cooldownIndex = 5;
            }

            if (_tp>0){
                wizzPandaCount[_tp] = wizzPandaCount[_tp] + 1;
            }

            if (_generation <= 1 && _tp != 1){
                require(gen0CreatedCount<GEN0_TOTAL_COUNT);
                gen0CreatedCount++;
            }
        }

        Panda memory _panda = Panda({
            genes: _genes,
            birthTime: uint64(now),
            cooldownEndBlock: 0,
            matronId: uint32(_matronId),
            sireId: uint32(_sireId),
            siringWithId: 0,
            cooldownIndex: cooldownIndex,
            generation: uint16(_generation)
        });
        uint256 newKittenId = pandas.push(_panda) - 1;

        require(newKittenId == uint256(uint32(newKittenId)));

        Birth(
            _owner,
            newKittenId,
            uint256(_panda.matronId),
            uint256(_panda.sireId),
            _panda.genes
        );

        _transfer(0, _owner, newKittenId);

        return newKittenId;
    }

    function setSecondsPerBlock(uint256 secs) external onlyCLevel {
        require(secs < cooldowns[0]);
        secondsPerBlock = secs;
    }
}

contract ERC721Metadata {

    function getMetadata(uint256 _tokenId, string) public view returns (bytes32[4] buffer, uint256 count) {
        if (_tokenId == 1) {
            buffer[0] = "Hello World! :D";
            count = 15;
        } else if (_tokenId == 2) {
            buffer[0] = "I would definitely choose a medi";
            buffer[1] = "um length string.";
            count = 49;
        } else if (_tokenId == 3) {
            buffer[0] = "Lorem ipsum dolor sit amet, mi e";
            buffer[1] = "st accumsan dapibus augue lorem,";
            buffer[2] = " tristique vestibulum id, libero";
            buffer[3] = " suscipit varius sapien aliquam.";
            count = 128;
        }
    }
}

contract PandaOwnership is PandaBase, ERC721 {

    string public constant name = "PandaEarth";
    string public constant symbol = "PE";

    bytes4 constant InterfaceSignature_ERC165 =
        bytes4(keccak256('supportsInterface(bytes4)'));

    bytes4 constant InterfaceSignature_ERC721 =
        bytes4(keccak256('name()')) ^
        bytes4(keccak256('symbol()')) ^
        bytes4(keccak256('totalSupply()')) ^
        bytes4(keccak256('balanceOf(address)')) ^
        bytes4(keccak256('ownerOf(uint256)')) ^
        bytes4(keccak256('approve(address,uint256)')) ^
        bytes4(keccak256('transfer(address,uint256)')) ^
        bytes4(keccak256('transferFrom(address,address,uint256)')) ^
        bytes4(keccak256('tokensOfOwner(address)')) ^
        bytes4(keccak256('tokenMetadata(uint256,string)'));

    function supportsInterface(bytes4 _interfaceID) external view returns (bool)
    {

        return ((_interfaceID == InterfaceSignature_ERC165) || (_interfaceID == InterfaceSignature_ERC721));
    }

    function _owns(address _claimant, uint256 _tokenId) internal view returns (bool) {
        return pandaIndexToOwner[_tokenId] == _claimant;
    }

    function _approvedFor(address _claimant, uint256 _tokenId) internal view returns (bool) {
        return pandaIndexToApproved[_tokenId] == _claimant;
    }

    function _approve(uint256 _tokenId, address _approved) internal {
        pandaIndexToApproved[_tokenId] = _approved;
    }

    function balanceOf(address _owner) public view returns (uint256 count) {
        return ownershipTokenCount[_owner];
    }

    function transfer(
        address _to,
        uint256 _tokenId
    )
        external
        whenNotPaused
    {

        require(_to != address(0));

        require(_to != address(this));

        require(_to != address(saleAuction));
        require(_to != address(siringAuction));

        require(_owns(msg.sender, _tokenId));

        _transfer(msg.sender, _to, _tokenId);
    }

    function approve(
        address _to,
        uint256 _tokenId
    )
        external
        whenNotPaused
    {

        require(_owns(msg.sender, _tokenId));

        _approve(_tokenId, _to);

        Approval(msg.sender, _to, _tokenId);
    }

    function transferFrom(
        address _from,
        address _to,
        uint256 _tokenId
    )
        external
        whenNotPaused
    {

        require(_to != address(0));

        require(_to != address(this));

        require(_approvedFor(msg.sender, _tokenId));
        require(_owns(_from, _tokenId));

        _transfer(_from, _to, _tokenId);
    }

    function totalSupply() public view returns (uint) {
        return pandas.length - 1;
    }

    function ownerOf(uint256 _tokenId)
        external
        view
        returns (address owner)
    {
        owner = pandaIndexToOwner[_tokenId];

        require(owner != address(0));
    }

    function tokensOfOwner(address _owner) external view returns(uint256[] ownerTokens) {
        uint256 tokenCount = balanceOf(_owner);

        if (tokenCount == 0) {

            return new uint256[](0);
        } else {
            uint256[] memory result = new uint256[](tokenCount);
            uint256 totalCats = totalSupply();
            uint256 resultIndex = 0;

            uint256 catId;

            for (catId = 1; catId <= totalCats; catId++) {
                if (pandaIndexToOwner[catId] == _owner) {
                    result[resultIndex] = catId;
                    resultIndex++;
                }
            }

            return result;
        }
    }

    function _memcpy(uint _dest, uint _src, uint _len) private view {

        for(; _len >= 32; _len -= 32) {
            assembly {
                mstore(_dest, mload(_src))
            }
            _dest += 32;
            _src += 32;
        }

        uint256 mask = 256 ** (32 - _len) - 1;
        assembly {
            let srcpart := and(mload(_src), not(mask))
            let destpart := and(mload(_dest), mask)
            mstore(_dest, or(destpart, srcpart))
        }
    }

    function _toString(bytes32[4] _rawBytes, uint256 _stringLength) private view returns (string) {
        var outputString = new string(_stringLength);
        uint256 outputPtr;
        uint256 bytesPtr;

        assembly {
            outputPtr := add(outputString, 32)
            bytesPtr := _rawBytes
        }

        _memcpy(outputPtr, bytesPtr, _stringLength);

        return outputString;
    }

}

/* ... all intermediate contracts unchanged ... */

contract ClockAuction is Pausable, ClockAuctionBase {

    bytes4 constant InterfaceSignature_ERC721 = bytes4(0x9a20483d);

    function ClockAuction(address _nftAddress, uint256 _cut) public {
        require(_cut <= 10000);
        ownerCut = _cut;

        ERC721 candidateContract = ERC721(_nftAddress);
        require(candidateContract.supportsInterface(InterfaceSignature_ERC721));
        nonFungibleContract = candidateContract;
    }

    function withdrawBalance() external {
        address nftAddress = address(nonFungibleContract);

        require(
            msg.sender == owner ||
            msg.sender == nftAddress
        );

        bool res = nftAddress.send(this.balance);
        require(res); // FIX: check low-level call result
    }

    /* rest of contract unchanged */
}

contract SaleClockAuctionERC20 is ClockAuction {

    event AuctionERC20Created(uint256 tokenId, uint256 startingPrice, uint256 endingPrice, uint256 duration, address erc20Contract);

    bool public isSaleClockAuctionERC20 = true;

    mapping (uint256 => address) public tokenIdToErc20Address;

    mapping (address => uint256) public erc20ContractsSwitcher;

    mapping (address => uint256) public balances;

    function SaleClockAuctionERC20(address _nftAddr, uint256 _cut) public
        ClockAuction(_nftAddr, _cut) {}

    /* ... unchanged code ... */

    function withdrawERC20Balance(address _erc20Address, address _to) external returns(bool res)  {
        require (balances[_erc20Address] > 0);
        require(msg.sender == address(nonFungibleContract));
        require(ERC20(_erc20Address).transfer(_to, balances[_erc20Address])); // FIX
        return true;
    }

    /* ... unchanged code ... */
}

contract PandaCore is PandaMinting {

    address public newContractAddress;

    function PandaCore() public {

        paused = true;

        ceoAddress = msg.sender;

        cooAddress = msg.sender;

    }

    /* ... unchanged code ... */

    function withdrawBalance() external onlyCFO {
        uint256 balance = this.balance;

        uint256 subtractFees = (pregnantPandas + 1) * autoBirthFee;

        if (balance > subtractFees) {

            require(cfoAddress.send(balance - subtractFees)); // FIX: check low-level call result
        }
    }
}
```
