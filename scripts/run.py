#!/usr/bin/env python
# coding=utf-8
"""
    File:
        run.py

    Description:
        Simple python routine to measure time for
    PMR3100 line follower competition

    Author:
        Felipe Gomes de Melo <felipegmelo@usp.br>
"""

import rospy
import numpy as np
from gazebo_msgs.srv import GetModelState
from std_srvs.srv import Empty

ANTEPARO_X = 0.90
ANTEPARO_Y = 1.075

DIST_TRHESHOLD = 0.5
VEL_TRHESHOLD = 5e-3


def get_model_state():
    rospy.wait_for_service("gazebo/get_model_state")
    try:
        get_state = rospy.ServiceProxy("gazebo/get_model_state", GetModelState)
        resp = get_state("meu_primeiro_robo", "")

        distancia = np.hypot(
            ANTEPARO_X - resp.pose.position.x - rospy.get_param("/meia_largura"),
            ANTEPARO_Y - resp.pose.position.y,
        )
        velocidade = np.hypot(resp.twist.linear.x, resp.twist.linear.y)
        return distancia, velocidade
    except rospy.ServiceException as e:
        print("Service call failed: %s" % e)


def reset_world():
    rospy.wait_for_service("gazebo/reset_world")
    try:
        reset = rospy.ServiceProxy("gazebo/reset_world", Empty)
        reset()
    except rospy.ServiceException as e:
        print("Service call failed: %s" % e)


def start_time():
    rospy.wait_for_service("gazebo/unpause_physics")
    try:
        reset = rospy.ServiceProxy("gazebo/unpause_physics", Empty)
        reset()
    except rospy.ServiceException as e:
        print("Service call failed: %s" % e)


def stop_time():
    rospy.wait_for_service("gazebo/pause_physics")
    try:
        reset = rospy.ServiceProxy("gazebo/pause_physics", Empty)
        reset()
    except rospy.ServiceException as e:
        print("Service call failed: %s" % e)


def main():

    rospy.init_node("cronometro")
    rate = rospy.Rate(100)  # 100hz

    rospy.wait_for_service("gazebo/get_model_state")
    rospy.wait_for_service("gazebo/unpause_physics")
    rospy.wait_for_service("gazebo/reset_world")

    stop_time()
    reset_world()
    start_time()

    rospy.sleep(0.1)
    inicio = rospy.get_time()
    rospy.loginfo("Começo da contagem de tempo!")

    while not rospy.is_shutdown():
        dist, vel = get_model_state()

        rospy.loginfo_throttle(
            5, f"Tempo {rospy.get_time() - inicio:.3f} D: {dist:.3f} V: {vel:.3f}"
        )

        if dist < DIST_TRHESHOLD and vel < VEL_TRHESHOLD:
            fim = rospy.get_time()
            delta = fim - inicio
            rospy.loginfo(f" => Fim da tomada de tempo!")
            rospy.loginfo(f"Distância: {dist:.03f}")
            rospy.loginfo(f"Tempo: {delta:.03f}")
            break

        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        pass
