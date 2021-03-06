from math import ceil


class State(object):
    pass


class SlowStart(object):

    def next(self, event, window):
        if event.name == "timeout":
            window.ssthresh = ceil(window.cwnd / 2)
            window.cwnd = window.MSS
            window.dup_ack_count = 0
            window.retansmit_missing_segments()
            return State.slow_start

        elif event.name == "new_ack":
            window.cwnd += window.MSS
            window.dup_ack_count = 0
            if window.cwnd >= window.ssthresh:
                return State.congestion_avoidance
            window.transmit_as_allowed()
            return State.slow_start

        elif event.name == "dup_ack":
            window.dup_ack_count += 1
            return State.slow_start

        elif event.name == "triple_ack":
            window.ssthresh = ceil(window.cwnd / 2)
            window.cwnd = window.ssthresh + 3 * window.MSS
            window.retansmit_missing_segments()
            return State.fast_recovery
        raise Exception("Slow start got weird event")


class CongestionAvoidance(object):

    def next(self, event, window):
        if event.name == "timeout":
            window.ssthresh = ceil(window.cwnd / 2)
            window.cwnd = window.MSS
            window.dup_ack_count = 0
            window.retansmit_missing_segments()
            return State.slow_start

        elif event.name == "new_ack":
            window.cwnd += window.MSS * round(window.MSS / window.cwnd, -1)
            window.dup_ack_count = 0
            window.transmit_as_allowed()
            return State.congestion_avoidance

        elif event.name == "dup_ack":
            window.dup_ack_count += 1
            return State.congestion_avoidance

        elif event.name == "triple_ack":
            window.ssthresh = ceil(window.cwnd / 2)
            window.cwnd = window.ssthresh + 3 * window.MSS
            window.retansmit_missing_segments()
            return State.fast_recovery

        raise Exception("Slow start got weird event")


class FastRecovery(object):

    def next(self, event, window):
        if event.name == "timeout":
            window.ssthresh = ceil(window.cwnd / 2)
            window.cwnd = window.MSS
            window.dup_ack_count = 0
            window.retansmit_missing_segments()
            return State.slow_start

        elif event.name == "new_ack":
            window.cwnd = window.ssthresh
            window.dup_ack_count = 0
            return State.congestion_avoidance

        elif event.name == "dup_ack":
            window.cwnd = window.cwnd + window.MSS
            return State.fast_recovery

        elif event.name == "triple_ack":
            window.cwnd += window.MSS
            return State.fast_recovery

State.slow_start = SlowStart()
State.congestion_avoidance = CongestionAvoidance()
State.fast_recovery = FastRecovery()
