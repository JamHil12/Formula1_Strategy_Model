using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Windows;
using System.Windows.Controls;

namespace F1_Strategy_Interface
{
    /// <summary>
    /// Interaction logic for Task_FindOptimalPitStopLaps.xaml
    /// </summary>
    public partial class Task_FindOptimalPitStopLaps : Page
    {
        // argX's will store the user's chosen inputs
        private string numLapsCompleted;
        private string numLapsRace;
        private string pitstopTime;
        private string currentTyre;
        private string currentTyreAge;
        private string needToUseDifferentTyre;
        private string maxNumPitstops;
        private string baseLapTime;
        private string fuelEffect;
        private string softQuadCoeff;
        private string softLinCoeff;
        private string mediumPaceDeficit;
        private string mediumQuadCoeff;
        private string mediumLinCoeff;
        private string hardPaceDeficit;
        private string hardQuadCoeff;
        private string hardLinCoeff;

        private PythonProcUtilities pythonProcUtilities = new PythonProcUtilities();

        /// <summary>
        /// Initialize the page
        /// </summary>
        public Task_FindOptimalPitStopLaps()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Tells the 'Home' button to send the user to the home page
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ButtonRetHomeClick(object sender, RoutedEventArgs e)
        {
            // View Home Page
            Home pg_Home = new Home();
            this.NavigationService.Navigate(pg_Home);
        }

        /// <summary>
        /// Updates a text block according to the input string
        /// </summary>
        /// <param name="str"> String, the text which the text block will display when this method runs. </param>
        private void UpdateText(string str)
        {
            Dispatcher.Invoke(() =>
            {
                Container.Children.OfType<TextBlock>().Cast<TextBlock>().ToList().ForEach(textblock =>
                {
                    textblock.Text = str;
                });
            });
        }

        /// <summary>
        /// Runs data validation on the user's inputs to check that they are OK to pass into Python
        /// </summary>
        private bool ValidateArgs()
        {
            bool validationPassed = false;  // Validation is assumed to have failed unless all the conditions in the following if statement are checked and OK
            if (!uint.TryParse(numLapsCompleted, out _))
            {
                UpdateText("Error: The total number of laps completed must be a non-negative integer.");
            }
            else if (!uint.TryParse(numLapsRace, out _) || numLapsRace == "0")
            {
                UpdateText("Error: The total number of laps in the race must be a positive integer.");
            }
            else if (Convert.ToInt32(numLapsCompleted) >= Convert.ToInt32(numLapsRace))
            {
                UpdateText("Error: The total number of laps completed must be less than the total number of laps in the race.");
            }
            else if (!float.TryParse(pitstopTime, out _) || (float.TryParse(pitstopTime, out _) && Convert.ToSingle(pitstopTime) < 0))
            {
                UpdateText("Error: The pitstop time loss must be a non-negative number.");
            }
            else if (!uint.TryParse(currentTyreAge, out _))
            {
                UpdateText("Error: The current tyre age must be a non-negative integer.");
            }
            else if (Convert.ToInt32(currentTyreAge) > Convert.ToInt32(numLapsRace))
            {
                UpdateText("Error: The current tyre age must be at most the total number of laps completed.");
            }
            else if (!uint.TryParse(maxNumPitstops, out _) || (uint.TryParse(maxNumPitstops, out _) && Convert.ToInt32(maxNumPitstops) > 4))
            {
                UpdateText("Error: The maximum number of pitstops must be an integer between 0 and 4.");
            }
            else if (!float.TryParse(baseLapTime, out _) || (float.TryParse(baseLapTime, out _) && Convert.ToSingle(baseLapTime) < 0))
            {
                UpdateText("Error: The base lap time must be a non-negative number.");
            }
            else if (!float.TryParse(fuelEffect, out _) || (float.TryParse(fuelEffect, out _) && Convert.ToSingle(fuelEffect) < 0))
            {
                UpdateText("Error: The fuel effect must be a non-negative number.");
            }
            else if (!float.TryParse(softQuadCoeff, out _))
            {
                UpdateText("Error: The soft tyre quadratic coefficient must be a number.");
            }
            else if (!float.TryParse(softLinCoeff, out _))
            {
                UpdateText("Error: The soft tyre linear coefficient must be a number.");
            }
            else if (!float.TryParse(mediumPaceDeficit, out _))
            {
                UpdateText("Error: The medium tyre pace deficit must be a number.");
            }
            else if (!float.TryParse(mediumQuadCoeff, out _))
            {
                UpdateText("Error: The medium tyre quadratic coefficient must be a number.");
            }
            else if (!float.TryParse(mediumLinCoeff, out _))
            {
                UpdateText("Error: The medium tyre linear coefficient must be a number.");
            }
            else if (!float.TryParse(hardPaceDeficit, out _))
            {
                UpdateText("Error: The hard tyre pace deficit must be a number.");
            }
            else if (!float.TryParse(hardQuadCoeff, out _))
            {
                UpdateText("Error: The hard tyre quadratic coefficient must be a number.");
            }
            else if (!float.TryParse(hardLinCoeff, out _))
            {
                UpdateText("Error: The hard tyre linear coefficient must be a number.");
            }
            else
            {
                validationPassed = true;
            }
            return validationPassed;
        }

        /// <summary>
        /// Runs the relevant Python script when the Run button is clicked
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ButtonRunClick(object sender, RoutedEventArgs e)
        {
            if (currentTyreListBox.SelectedValue == null)
            {
                UpdateText("Error: one or more of the required inputs is missing.");
                return;
            }

            numLapsCompleted = numLapsCompletedTextBox.Text.ToString();
            numLapsRace = numLapsRaceTextBox.Text.ToString();
            pitstopTime = pitstopTimeTextBox.Text.ToString();
            currentTyre = currentTyreListBox.SelectionBoxItem.ToString();
            currentTyreAge = currentTyreAgeTextBox.Text.ToString();
            needToUseDifferentTyre = needToUseDifferentTyreCheckBox.IsChecked.ToString();
            maxNumPitstops = maxNumPitstopsTextBox.Text.ToString();
            baseLapTime = baseLapTimeTextBox.Text.ToString();
            fuelEffect = fuelEffectTextBox.Text.ToString();
            softQuadCoeff = softQuadCoeffTextBox.Text.ToString();
            softLinCoeff = softLinCoeffTextBox.Text.ToString();
            mediumPaceDeficit = mediumPaceDeficitTextBox.Text.ToString();
            mediumQuadCoeff = mediumQuadCoeffTextBox.Text.ToString();
            mediumLinCoeff = mediumLinCoeffTextBox.Text.ToString();
            hardPaceDeficit = hardPaceDeficitTextBox.Text.ToString();
            hardQuadCoeff = hardQuadCoeffTextBox.Text.ToString();
            hardLinCoeff = hardLinCoeffTextBox.Text.ToString();

            if (!ValidateArgs()) {
                return;
            }

            List<string> inputArgList = new List<string> {
                numLapsCompleted,
                numLapsRace,
                pitstopTime,
                currentTyre,
                currentTyreAge,
                needToUseDifferentTyre,
                maxNumPitstops,
                baseLapTime,
                fuelEffect,
                softQuadCoeff,
                softLinCoeff,
                mediumPaceDeficit,
                mediumQuadCoeff,
                mediumLinCoeff,
                hardPaceDeficit,
                hardQuadCoeff,
                hardLinCoeff
            };

            UpdateText("Running...please wait. A new window with the requested plot will appear once complete.");

            Process proc = pythonProcUtilities.RunPython("run_python_plot_optimal_race_strategies.bat", inputArgList, true);
            ThreadPool.QueueUserWorkItem(delegate {
                proc.Start();
                int pid = proc.Id;
                int waitTimeSeconds = 80;
                if (!proc.WaitForExit(waitTimeSeconds * 1000))
                {
                    pythonProcUtilities.KillProcess(pid);
                    UpdateText($"Process stopped: reached the {waitTimeSeconds} second limit.");
                }
                else
                {
                    UpdateText("Process completed.");
                }
            });
        }
    }
}
