import gym
from mcts_general.agent import MCTSAgent
from mcts_general.config import MCTSAgentConfig
from mcts_general.game import DiscreteGymGame
from RL.env import DeadlyHotelEnv

# configure agent
config = MCTSAgentConfig()
config.num_simulations = 200
agent = MCTSAgent(config)

# init game
episode=0
kill_success_num=0
kill_and_not_arrested_num=0
game = DiscreteGymGame(env=DeadlyHotelEnv())
state = game.reset()

done = False
reward = 0
# run a trajectory
while True:
    action = agent.step(game, state, reward, done)
    game.render(mode="console")

    print(action,reward)
    state, reward, done = game.step(action)

    if done:
        episode+=1

        if state[7]==0:
            kill_success_num+=1
        if len(state)==9:
            kill_and_not_arrested_num+=1

        print('episode:',episode)
        print('kill_success_num:',kill_success_num)
        print('kill_and_not_arrested_num:',kill_and_not_arrested_num)
        game.reset()


game.close()
