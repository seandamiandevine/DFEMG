from psychopy import visual, core, event, monitors, sound
import pandas as pd
from random import shuffle
from numpy.random import choice
import os
import datetime as dt
import pyfiglet

from fx.addOutput import addOutput, initCSV

def runTask(id, sex, age, _thisDir):
    """
    Risky decision-making task for Alexa's project
    fEMG triggers to be added for BIOPAC machine
    
    
    For question, contact Sean. 
    seandamiandevine@gmail.com
    """
    # Initialize datafile
    filename = _thisDir + os.sep + 'data' + os.sep + 'DFEMG_' + str(id)+'_'+str(dt.datetime.now()).replace(':','_')+'.csv'
    initCSV(filename, ['id', 'age', 'sex', 'trial', 'certainSide', 'riskySide', 'certainRew', 'riskyRew', 'probability', 
     'key_press', 'choice', 'RT', 'outcome', 'feedback', 'score', 'happiness', 'happinessRT', 'cardTime', 'choiceTime', 'fbTime', 'ITITime'])

    # Window setup
    win = visual.Window(
        size=[1920/2, 1080/2], fullscr=True, screen=0,
        allowGUI=False, allowStencil=False,
        monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='cm')

    # Set constants
    textCol      = [1, 1, 1]                      # font colour
    valCol       = [0, 0, .55]                    # reward colours
    fontH        = 1                              # font height
    trialdf      = pd.read_csv('outcomes.csv')    # outcome list
    nTrials      = len(trialdf)                   # number of trials
    loseRisk     = 0                              # amount gained (or lost) when risky option is lost
    choiceKeys   = ['left', 'right']              # keys to make choices
    ITI          = 2                              # ITI time in sec. 
    fbTime       = 1.5                            # feedback time in sec. 
    stimDir      = 'stim/'                        # directory where stimuli are located 
    maxPayout    = 5                              # amount all subjects earn at end, regardless of points
    hapFreq      = 5                              # number of trials between happiness scales
    
    # initialize trial components
    trialClock = core.Clock()
    certainRew = visual.TextStim(win, text="", height=3*fontH, color=valCol)
    riskyRew   = visual.TextStim(win, text="", height=3*fontH, color=valCol)
    riskyLoss  = visual.TextStim(win, text='$'+str(loseRisk), height=3*fontH, color=valCol)
    cardL      = visual.ImageStim(win, image="{}100.png".format(stimDir), pos=[-8, 0], units='cm', size=[8,12])
    cardR      = visual.ImageStim(win, image="{}100.png".format(stimDir), pos=[8, 0],  units='cm', size=[8,12])
    scoreBoard = visual.TextStim(win, text="", height=fontH, color=textCol, units='cm', pos=[-15, 15])
    feedback   = visual.TextStim(win, text="", height=3*fontH,color=textCol)
    fix        = visual.TextStim(win, text="+", height=3*fontH,color=textCol)
    winSound   = sound.Sound('{}Register.wav'.format(stimDir))
    loseSound  = sound.Sound('{}Click.wav'.format(stimDir))
    endScreen  = visual.TextStim(win, text="", height=fontH, color=textCol)
    hapPrompt  = visual.TextStim(win, text="How happy are you at this moment?", height=fontH, color=textCol, pos=[0, 3])
    hapSlider  = visual.RatingScale(win, low=1, high=10, markerStart=5, leftKeys='left', rightKeys='right', acceptKeys='space', marker='circle', scale=None, labels=['Very unhappy','Very happy'])

    #--------------------------------------Start Task-----------------------------------------
    win.mouseVisible=True

    # Test trials
    trialdf['CertainSide'] = ['R']*int(nTrials/2) + ['L']*int(nTrials/2)
    trialdf                = trialdf.sample(frac=1).reset_index(drop=True) # shuffle trial list
    score = 0
    for t in range(nTrials):
        thisCertain = trialdf.Certain.iloc[t]
        thisRisky   = trialdf.Risky.iloc[t]
        thisProb    = trialdf.Probability.iloc[t]
        certainSide = trialdf.CertainSide.iloc[t]
        riskySide   = 'R' if certainSide=='L' else 'L'

        startTime = trialClock.getTime()
        
        # 1. Display cards
        cardTime        = trialClock.getTime()
        certainRew.text = '$'+str(thisCertain)
        riskyRew.text   = '$'+str(thisRisky)
        scoreBoard.text = 'Your total:\n ${}'.format(round(score, 2))
        if certainSide=='R':
            cardL.image    = '{}{}_{}.png'.format(stimDir, int(thisProb*100), int(round((1-thisProb)*100)))
            cardR.image    = '{}100.png'.format(stimDir)
            certainRew.pos = [cardR.pos[0], cardR.pos[1]+8]
            riskyRew.pos   = [cardL.pos[0], cardL.pos[1]-8]
            riskyLoss.pos  = [cardL.pos[0], cardL.pos[1]+8]
        else: 
            cardR.image    = '{}{}_{}.png'.format(stimDir, int(thisProb*100), int(round((1-thisProb)*100)))
            cardL.image    = '{}100.png'.format(stimDir)
            certainRew.pos = [cardL.pos[0], cardL.pos[1]+8]
            riskyRew.pos   = [cardR.pos[0], cardR.pos[1]-8]
            riskyLoss.pos  = [cardR.pos[0], cardR.pos[1]+8]
        cardL.draw()
        cardR.draw()
        certainRew.draw()
        riskyRew.draw()
        riskyLoss.draw()
        scoreBoard.draw()
        win.flip()
        key_press   = event.waitKeys(keyList = choiceKeys)
        choiceTime  = trialClock.getTime()
        RT          = choiceTime - cardTime
        response    = key_press[0]
        if response == choiceKeys[0] and certainSide=='L':
            choiceRC = 'certain'
            reward   = thisCertain
        elif response == choiceKeys[1] and certainSide=='R':
            choiceRC = 'certain'
            reward   = thisCertain
        else: 
            choiceRC = 'risky'
            reward   = choice([thisRisky,loseRisk], 1, [thisProb, 1-thisProb])[0]
        score+=reward

        # 3. Feedback
        feedbackTime   = trialClock.getTime()
        feedback.text  = '+${}'.format(reward)
        if reward==0:
            feedback.color='red'
            loseSound.play()
        else: 
            feedback.color='green'
            winSound.play()
        feedback.draw()
        win.flip()
        core.wait(fbTime)
        win.flip()

        # 4. Happiness slider 
        if t>0 and t%hapFreq==0:
            while hapSlider.noResponse:
                hapPrompt.draw()
                hapSlider.draw()
                win.flip()
            happiness   = hapSlider.getRating()
            happinessRT = hapSlider.getRT()
            hapSlider.reset()
        else: 
            happiness   = 'NA'
            happinessRT = 'NA'

        # 5. ITI
        ITITime = trialClock.getTime()
        fix.draw()
        win.flip()
        core.wait(ITI)
        win.flip()

        # Save output
        out = [id, age, sex, t, certainSide, riskySide, thisCertain, thisRisky, thisProb, 
            response, choiceRC, RT, reward, feedback.text, score, happiness, happinessRT, cardTime, choiceTime, feedbackTime, ITITime]
        addOutput(filename, out)
   
    # Show end screen
    endScreen.text='Thank you for completing our study!\n\nYou earned {} points, which translates to ${}.\n\nSee the experimenter for further details.'.format(round(score,2), maxPayout)
    endScreen.draw()
    win.flip()
    event.waitKeys(keyList = ['escape'])

# Run task
os.system('clear')
print(pyfiglet.figlet_format("DFEMG STUDY"))
id  = input('Please enter the SUBJECT ID NUMBER: ')
age = input("Please enter the subject's AGE: ")
sex = input("Please enter the subject's SEX: ")
print('Good luck!')
# sex='M'
# age='25'
# id = '999'

runTask(id, str(sex), str(age), os.getcwd())
