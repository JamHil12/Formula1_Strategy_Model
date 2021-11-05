using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace F1_Strategy_Interface
{
    /// <summary>
    /// Interaction logic for Home.xaml
    /// </summary>
    public partial class Home : Page
    {
        public Home()
        {
            InitializeComponent();
        }

        private void Button_Plot_Prev_Race_Click(object sender, RoutedEventArgs e)
        {
            // Go to the PlotPreviousRaceLapTimes page
            Task_PlotPreviousRaceLapTimes pg_PlotPreviousRaceLapTimes = new Task_PlotPreviousRaceLapTimes();
            this.NavigationService.Navigate(pg_PlotPreviousRaceLapTimes);
        }

        private void Button_Plot_Optimal_Pit_Laps_Click(object sender, RoutedEventArgs e)
        {
            // Go to the FindOptimalPitStopLaps page
            Task_FindOptimalPitStopLaps pg_FindOptimalPitStopLaps = new Task_FindOptimalPitStopLaps();
            this.NavigationService.Navigate(pg_FindOptimalPitStopLaps);
        }
    }
}
