from time import sleep


def run(job):
    job.reset()
    job.status = 'L.STR'
    job.save()

    job.status = 'L.CPL'
    job.save()
