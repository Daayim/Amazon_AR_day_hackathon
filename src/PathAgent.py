# Custom imports to assist in interfacing with the simulator
from src.DriveInterface import DriveInterface
from src.DriveState import DriveState
from src.Constants import DriveMove, SensorData


class PathAgent(DriveInterface):

    def __init__(self, game_id: int, is_advanced_mode: bool):
        """
        Constructor for PathAgent

        Arguments:
        game_id -- a unique value passed to the player drive, you do not have to do anything with it, but will have access.
        is_advanced_mode -- boolean to indicate if 
        """
        self.game_id  = game_id
        self.need_to_find_target_pod = is_advanced_mode
        

    # This is the main function the simulator will call each turn 
    def get_next_move(self, sensor_data: dict) -> DriveMove:
        """
        Main function for YourAgent. The simulator will call this function each loop of the simulation to see what your agent's
        next move would be. You will have access to data about the field, your robot's location, other robots' locations and more
        in the sensor_data dict arguemnt.

        Arguments:
        sensor_data -- a dict with state information about other objects in the game. The structure of sensor_data is shown below:
            sensor_data = {
                SensorData.FIELD_BOUNDARIES: [[-1, -1], [-1, 0], ...],  
                SensorData.DRIVE_LOCATIONS: [[x1, y1], [x2, y2], ...], 
                SensorData.POD_LOCATIONS: [[x1, y1], [x2, y2], ...],
                SensorData.PLAYER_LOCATION: [x, y],
                SensorData.GOAL_LOCATION: [x, y], (Advanced Mode)
                SensorData.TARGET_POD_LOCATION: [x, y], # Only used for Advanced mode
                SensorData.DRIVE_LIFTED_POD_PAIRS: [[drive_id_1, pod_id_1], [drive_id_2, pod_id_2], ...] (Only used in Advanced mode for seeing which pods are currently lifted by drives)

            }

        Returns:
        DriveMove - return value must be one of the enum values in the DriveMove class:
            DriveMove.NONE – Do nothing
            DriveMove.UP – Move 1 tile up (positive y direction)
            DriveMove.DOWN – Move 1 tile down (negative y direction)
            DriveMove.RIGHT – Move 1 tile right (positive x direction)
            DriveMove.LEFT – Move 1 tile left (negative x direction)
            
            (Advanced mode only)
            DriveMove.LIFT_POD – If a pod is in the same tile, pick it up. The pod will now move with the drive until it is dropped
            DriveMove.DROP_POD – If a pod is in the same tile, drop it. The pod will now stay in this position until it is picked up

        """

        currLocation = tuple(sensor_data[SensorData.PLAYER_LOCATION])
        goalLocation = tuple(sensor_data[SensorData.GOAL_LOCATION])
        driveLocations = set(tuple(loc) for loc in sensor_data[SensorData.DRIVE_LOCATIONS])
        targetPodLocation = tuple(sensor_data[SensorData.TARGET_POD_LOCATION]) if sensor_data[SensorData.TARGET_POD_LOCATION] is not None else None
        driveLiftedPodPairs = sensor_data[SensorData.DRIVE_LIFTED_POD_PAIRS]

        try:
            if self.need_to_find_target_pod:
                if targetPodLocation:
                    if currLocation == targetPodLocation:
                        return DriveMove.LIFT_POD
                    return self.move_towards_target(currLocation, targetPodLocation, driveLocations)
                
                # Check if the pod has been lifted
                is_pod_lifted = any(pair[0] == self.game_id for pair in driveLiftedPodPairs)
                
                if is_pod_lifted:
                    if currLocation == goalLocation:
                        return DriveMove.DROP_POD
                    return self.move_towards_target(currLocation, goalLocation, driveLocations)

            return self.move_towards_target(currLocation, goalLocation, driveLocations)
        except Exception as e:
            raise Exception(f"get_next_move in PathAgent failed: {str(e)}")

    def move_towards_target(self, currLocation, targetLocation, driveLocations) -> DriveMove:
        dx, dy = targetLocation[0] - currLocation[0], targetLocation[1] - currLocation[1]
        moves = []
        if dx > 0: moves.append(DriveMove.RIGHT)
        if dx < 0: moves.append(DriveMove.LEFT)
        if dy > 0: moves.append(DriveMove.UP)
        if dy < 0: moves.append(DriveMove.DOWN)

        for move in moves:
            new_location = {
                DriveMove.RIGHT: (currLocation[0] + 1, currLocation[1]),
                DriveMove.LEFT: (currLocation[0] - 1, currLocation[1]),
                DriveMove.UP: (currLocation[0], currLocation[1] + 1),
                DriveMove.DOWN: (currLocation[0], currLocation[1] - 1)
            }[move]
            if new_location not in driveLocations:
                return move
        return DriveMove.NONE
