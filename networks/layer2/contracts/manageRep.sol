// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./NoScoring.sol";
import "./SafeMath.sol" ;
import "./Math.sol" ;


// for now this is to calculate the objective automated reputation  aka evaluate a trainer's work in the current task => deterministic reputation
contract ManageReputation {


    // imported libraries 
    using SafeMath for uint256;
    using Math for *; 

    // events
    event performanceMeasured(uint256,uint256);
    event scoresFetched(int256[]);  
    event scoreTrainerFetched(int256); 
    event recencyGot(uint256);
    event interactionsTP(uint256,uint256);

    // Calculation

    //uint _scale = 10**17; 
    uint _scale = 1000000 ;
    uint256 _scaleScore = 1e18 ;
    uint256 _scaleDifference = _scaleScore/_scale ;


    // Imported contracts
    NoScore public  taskContractInstance ;
    mapping(address => mapping(address => uint256)) public _overallPositiveHistory;   // address TP => address trainer => value
    mapping(address => mapping(address => uint256)) public _overallNegativeHistory;   // address TP => address trainer => value
    
    
    mapping(uint => mapping(address => uint256)) public _roundPositivePerformance;   // task id => trainer => + performance
    mapping(uint => mapping(address => uint256)) public _roundNegativePerformance;   // task id => trainer => - performance


    constructor(address _taskContractAddress){
        taskContractInstance = NoScore(_taskContractAddress);
    }
   
    // it is based on the historical interactions between a task publisher and a trainer 
    // when we 
    function automatedReputation(address _taskPublisher , address _trainer) public returns(uint256)
     {
        uint256 _result = 0;
        if ((_overallPositiveHistory[_taskPublisher][_trainer]+_overallNegativeHistory[_taskPublisher][_trainer]) != 0)
        {
       uint256 _alpha = _overallPositiveHistory[_taskPublisher][_trainer]/(_overallPositiveHistory[_taskPublisher][_trainer]+_overallNegativeHistory[_taskPublisher][_trainer]);
       uint256 _interactionsTpTa = taskContractInstance.interactionTaskPublisherTrainer(_taskPublisher , _trainer) ;
       uint256 _interactionsTp = 0 ;
       uint[] memory _allTasks = taskContractInstance.allTasksOfTaskPublisher(_taskPublisher) ;
       address[] memory _allTrainers = taskContractInstance.getAllTrainers() ;
       for (uint i = 0; i < _allTasks.length; i++){
        for (uint j = 0 ; j < _allTrainers.length ; j++)
           {
            if ( taskContractInstance.isTrainerInTask(_allTasks[i],_allTrainers[j]) == true ){
            _interactionsTp += taskContractInstance.interactionTaskPublisherTrainer(_taskPublisher , _allTrainers[j]) ;
           }
           }
       }
       emit interactionsTP(_interactionsTpTa,_interactionsTp);
        // balanced uncertainty , have not found anything that can help me determine its right value so 0.5
        uint256 _uncertainty = 5*_scaleScore ;
        uint256 _u = 10*_scale-(_interactionsTpTa*_scale / _interactionsTp) ;
        _result = ((10*_scale-_u)*_alpha + _uncertainty*_u)/_scale ;
        }

    //    return ((10*_scale-_u)*_alpha + _uncertainty*_u)/_scale ;
    return _result;
     }

    function measurePerformance(uint _taskId, uint _startingRound , uint _finishingRound, address _trainer , string memory _method) public returns(uint256 , uint256)
     {
        int256[] memory _roundScores ;
        uint256 _goodInteractions = 0 ;
        uint256 _badInteractions = 0 ;
        int256 score ;
        uint256 _taskParticipationLevel;
        int256 _weight ;
        for (uint i = _startingRound; i < _finishingRound; i++)
        { 
            // get the round's scores
            _roundScores  = taskContractInstance.getRoundScores(_taskId, i);
            emit scoresFetched(_roundScores);
            
            // get the trainer'score and recency
            // we assume weight of good intercation 0.4 and bad 0.6 for now
            score = taskContractInstance.getScoreWorker(_taskId, i , _trainer);
            emit scoreTrainerFetched(score);

            uint256 _recency = uint256(Math.tanh(int256(i+1),int256(_scale)));
            emit recencyGot(_recency);
            // what values to give to _goodWeight and _badWeight
            uint256 _goodWeight = 4 ;
            // what are the considered complexity level values
            uint256 _complexity = 5;
            // based on the interaction effect ( good or bad ) 
            bool interaction_state = detect_interaction(score,_roundScores,_method) ;
            if (interaction_state == true ){
                // good behaviour
                // u need to scale these in python by dividing on 1e18 **3 . I think so 
            _goodInteractions+=abs(score)*_recency*_goodWeight*_complexity ;
            }else {
                // bad behaviour
                // u need to scale these in python by dividing on 1e18 **3 . I think so 
                // it should be -abs(score) 
            _badInteractions+=abs(score)*_recency*(10-_goodWeight)*_complexity ;
            }       
        }
        //return (_goodInteractions,_badInteractions) ;
        //updateRepuation(_taskId,_trainer,_goodInteractions,_badInteractions);

        // // the scale will be the score's factor aka 1e18
        // _goodInteractions = _goodInteractions /(_scale*_scale*10);
        // _badInteractions = _badInteractions /(_scale*_scale*10);

        // store the current time slot performance 
        _roundPositivePerformance[_taskId][_trainer]+= _goodInteractions ;
        _roundNegativePerformance[_taskId][_trainer]+= _badInteractions ;

        // at the end of the task update the overall historical positive and negative interactions

        NoScore.Task memory _taskDetails = taskContractInstance.getTaskById(_taskId);
        address _taskPublisher = _taskDetails.publisher ;
        if(_finishingRound == _taskDetails.maxRounds)
        {        // the weight of the added performance during the task depends on the number of the current task
            _taskParticipationLevel = taskContractInstance.taskParticipationLevel(_taskId , _trainer);
            _weight = Math.tanh(int256(taskContractInstance.totalNumberOfTasksWithPublisher(_trainer, _taskPublisher)),int256(_scale));    //*  this part am not sure how to do it       int256(_taskParticipationLevel) ;
            _overallPositiveHistory[_taskPublisher][_trainer] += uint256(_weight)*_roundPositivePerformance[_taskId][_trainer]; 
            _overallNegativeHistory[_taskPublisher][_trainer] += uint256(_weight)*_roundNegativePerformance[_taskId][_trainer]; 
        }
        emit performanceMeasured(_goodInteractions, _badInteractions);
        return (_goodInteractions, _badInteractions) ;
    }
    // we give an interaction score and based on the other scores we say if the interaction is good or bad
    // depends on the case : multi krum or the 2 others
    
    function detect_interaction(int _score , int[] memory _scores , string memory _method) public pure returns (bool) {
        
        uint sum = 0;
        for (uint i = 0; i < _scores.length; i++) {
            sum += abs(_scores[i]);
        } 
    
    
        uint _avgScore =  sum / _scores.length;
    

        if (bytes(_method).length == bytes("similarity").length && keccak256(abi.encodePacked(_method)) == keccak256(abi.encodePacked("similarity"))) {
            if(abs(_score) <= _avgScore) {
                return true;
                                    }
            else {
                return false;
                }
          
            } else
        // considered bad interaction if the score is negative and its absolute value is bigger then the average
         {
            if(abs(_score) > _avgScore && _score <= 0 ) {
                return false;
            }
            else  {
                return true;
            }
        }        
    }

// function abs(int x) private pure returns (uint) {
//     return x >= 0 ? x : -x;
// }

function abs(int256 x) private pure returns (uint256) {
    return x >= 0 ? uint256(x) : uint256(-x);
}

// local reputation 
    function _localRepuation(uint _taskId, uint _startingRound , uint _finishingRound, address _trainer , string memory _method ) public returns (uint256){
        ( uint256 _goodInteractions , uint256 _badInteractions ) = measurePerformance(_taskId,_startingRound,_finishingRound,_trainer,_method); // scaleScore

        uint256 _subjectiveRep = automatedReputation(taskContractInstance.getAllTasks()[_taskId].publisher,_trainer); // scaleScore
        // // it has to be chosen wisely
        uint256 _weight = 8 ;
        uint256 _localRep = (10-_weight)*_subjectiveRep + (_weight)*(_goodInteractions+_badInteractions) ;
        return _localRep / 10 ;  // scaleScore 
        // return _goodInteractions+_badInteractions ;
        // return _localRep ;  // scaleScore * 10 

    }

    // // u need to figure out what s the best way to calculate the weight here
    // function updateRepuation(uint _taskId, address _worker , uint256 _goodInteractions , uint256 _badInteractions ) public  {
    //     // the weight to be assigned to the performance
    //     // if it is a good performance more weight is assigned to the previous reputation
    //     // if it is a bad performance less weight is assigned to the previous reputation means that the reputation will drop more and this is done to discourage trainers from performing poorly
    //     uint256 _performance = _goodInteractions + _badInteractions ;
    //     uint256 _weight ;
    //     uint256 _prevRep ;
    //     uint256 _newRep ;
    //     uint256 _factor = 10**17;
    //     // calculate the assigned weight and updateReputation
    //     if(_goodInteractions >= _badInteractions ){
    //         _newRep = _weight.mul(_prevRep).add(_performance.mul(_factor.sub(_weight)));
    //     }
    //     else{
    //         _newRep = _factor.sub(_weight).mul(_prevRep).sub(_performance.mul(_weight));
    //     }
    //     //taskContractInstance.setReputation(_taskId,_worker,_newRep); 
    // }

        // u need to figure out what s the best way to calculate the weight here
    function updateRepuation(uint _taskId,uint _startingRound , uint _finishingRound, address _addr , string memory _method  ) public  {
        // the weight to be assigned to the performance
        // if it is a good performance more weight is assigned to the previous reputation
        // if it is a bad performance less weight is assigned to the previous reputation means that the reputation will drop more and this is done to discourage trainers from performing poorly
        NoScore.Trainer[] memory _allReputations = taskContractInstance.getAllReputations();
        uint _sum = 0;
        for (uint i = 0; i < _allReputations.length; i++) {
            _sum += _allReputations[i]._reputation;
        }   
        uint _avgRep =  _sum / _allReputations.length; // scaleScore 
        uint256 _localRep =  _localRepuation(_taskId,_startingRound,_finishingRound,_addr,_method); // scaleScore
        uint256 _weight = uint256(Math.tanh(int256(taskContractInstance.totalParticipationLevel(_addr)),int256(_scale))) ;
        // uint256 _prevRep = taskContractInstance.getReputation(_addr);
        // uint256 _newRep ;
        // // calculate the assigned weight and updateReputation
        // if(_localRep >= _avgRep ){
        //     _newRep = (_weight*_prevRep + _localRep*(10*_scale-_weight)) / _scale;
            
        // }
        // else{
        //     _newRep = ((10*_scale-_weight)*_prevRep + _localRep*_weight) / _scale;
        //     // scaleScore
        // }
        // taskContractInstance.setReputation(_addr,_newRep); 
        // taskContractInstance.setReputation(_addr,_localRep); 

        uint256 eh = 0;
        eh = taskContractInstance.totalParticipationLevel(_addr) ;
        taskContractInstance.setReputation(_addr,eh); 

    }
}