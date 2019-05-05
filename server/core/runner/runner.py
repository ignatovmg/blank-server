import logging
from time import sleep

logger = logging.getLogger('core')


def run_job(job):
    """
    Sample job runner. Replace with your own.

    :param `.models.Job` job: Job Object to use
    """
    job.status = 'L.STR'
    job.save()
    sleep(5)

    job.status = 'L.PRE'
    job.save()

    sleep(10)
    out_dir = job.get_output_dir()
    out_dir.mkdir_p()
    out_file = out_dir.joinpath('output.txt')
    out_file.write_text(f'Job {job.job_id} output')

    job.status = 'L.CPL'
    job.save()
