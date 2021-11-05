using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows;
using System.Windows.Controls;

namespace F1_Strategy_Interface
{
    /// <summary>
    /// Interaction logic for Task_PlotPreviousRaceLapTimes.xaml
    /// </summary>
    public partial class Task_PlotPreviousRaceLapTimes : Page
    {
        private string year;  // The user's chosen year
        private string race;  // The user's chosen race
        private string driver;  // The user's chosen driver

        private PythonProcUtilities pythonProcUtilities = new PythonProcUtilities();

        /// <summary>
        /// Initialize the page
        /// </summary>
        public Task_PlotPreviousRaceLapTimes()
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
            NavigationService.Navigate(pg_Home);
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
        /// Runs the relevant Python script when the user clicks the 'Run' button
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ButtonRunClick(object sender, RoutedEventArgs e)
        {
            if (yrListBox.SelectedValue == null || rndListBox.SelectedValue == null || driverListBox.SelectedValue == null)
            {
                UpdateText("Error: one or more of the required inputs is missing.");
                return;
            }

            year = yrListBox.SelectionBoxItem.ToString();

            // Use regex to extract the round number from the user's chosen race  
            string pattern = @"^([^\:])+";
            Regex rg = new Regex(pattern);
            race = rg.Match(rndListBox.SelectionBoxItem.ToString()).ToString();

            driver = driverListBox.SelectionBoxItem.ToString();

            List<string> inputArgList = new List<string> { year, race, driver };

            UpdateText("Running...please wait. A new window with the requested plot will appear once complete.");

            Process proc = pythonProcUtilities.RunPython("run_python_plot_historical_race_lap_times.bat", inputArgList);
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
