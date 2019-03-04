import sys
import logging
import itertools
import asyncio
import contextlib
from asyncio.subprocess import PIPE


logging.basicConfig(format='%(funcName)s: %(message)s', level=logging.INFO)


async def print_coro():
    for i in itertools.count():
        logging.info("iteration number: %s", i)
        await asyncio.sleep(0.4)


async def subproc_coro(timeout: float):
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "producer.py", stderr=PIPE, stdout=PIPE
    )
    logging.info("started")
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as e:
        logging.info("child process didn't return within %.2f seconds", timeout)
        proc.terminate()
        logging.info("kindly asked child process to die, waiting for reaction")
        try:
            await asyncio.wait_for(proc.wait(), 1)
        except asyncio.TimeoutError:
            logging.info(
                "child not willing to die, guess there is"
                "nothing i can do about it on Windows"
            )
        else:
            logging.info("child processed obeyed the order")
    else:
        out, err = out.decode("utf-8").strip(), err.decode("utf-8").strip()
        print("--------------stdout:\n" + out)
        if err:
            print("--------------stderr:\n" + err)


async def main():
    done, pending = await asyncio.wait(
        [print_coro(), subproc_coro(15)],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    await asyncio.sleep(0.2)  # give loop time for clean-up


if __name__ == "__main__":
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    with contextlib.closing(loop):
        loop.run_until_complete(main())
