import subprocess

from criticality_core.config import (
    MODELS_DIR,
    CREATE_SERVICE,
    REMOVE_SERVICE,
    SET_POSE_SERVICE,
    QUAT_W,
)


class EntityManager:

    def _execute_service(self, cmd):

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return result

    # --------------------------------------------------

    def spawn_model(
        self,
        model_file,
        model_name,
        x,
        y,
        z,
    ):

        model_path = f"{MODELS_DIR}/{model_file}"

        cmd = [
            "gz",
            "service",
            "-s",
            CREATE_SERVICE,
            "--reqtype",
            "gz.msgs.EntityFactory",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            (
                f'sdf_filename: "{model_path}" '
                f'name: "{model_name}" '
                f'pose {{ '
                f'position {{ '
                f'x: {x} '
                f'y: {y} '
                f'z: {z} '
                f'}} '
                f'orientation {{ '
                f'w: {QUAT_W} '
                f'}} '
                f'}}'
            ),
        ]

        return self._execute_service(cmd)

    # --------------------------------------------------

    def move_model(
        self,
        model_name,
        x,
        y,
        z,
    ):

        cmd = [
            "gz",
            "service",
            "-s",
            f"{SET_POSE_SERVICE}/blocking",
            "--reqtype",
            "gz.msgs.Pose",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            (
                f'name: "{model_name}" '
                f'position {{ '
                f'x: {x} '
                f'y: {y} '
                f'z: {z} '
                f'}} '
                f'orientation {{ '
                f'w: {QUAT_W} '
                f'}}'
            ),
        ]

        return self._execute_service(cmd)

    # --------------------------------------------------

    def remove_model(
        self,
        model_name,
    ):

        cmd = [
            "gz",
            "service",
            "-s",
            REMOVE_SERVICE,
            "--reqtype",
            "gz.msgs.Entity",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            f'name: "{model_name}" type: MODEL',
        ]

        return self._execute_service(cmd)
