using System.Windows;
using System.Windows.Controls;

namespace F1_Strategy_Interface
{
    /// <summary>
    /// Interaction logic for Intro.xaml
    /// </summary>
    public partial class Intro : Page
    {
        public Intro()
        {
            InitializeComponent();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            // View Home Page
            Home pg_Home = new Home();
            this.NavigationService.Navigate(pg_Home);
        }
    }
}
