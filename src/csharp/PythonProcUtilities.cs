using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Management;
using System.Text;

namespace F1_Strategy_Interface
{
    /// <summary>
    /// Useful helper methods to control the Python processes called upon by the user
    /// </summary>
    public class PythonProcUtilities
    {
        /// <summary>
        /// Kills a process and any associated child processes
        /// </summary>
        /// <param name="pid"> Int, the id of the process to be killed </param>
        public void KillProcess(int pid)
        {
            ManagementObjectSearcher processSearcher = new ManagementObjectSearcher
              ("Select * From Win32_Process Where ParentProcessID=" + pid);
            ManagementObjectCollection processCollection = processSearcher.Get();

            if (processCollection != null)
            {
                foreach (ManagementObject mo in processCollection)
                {
                    KillProcess(Convert.ToInt32(mo["ProcessID"]));
                }
            }

            try
            {
                Process proc = Process.GetProcessById(pid);
                if (!proc.HasExited) proc.Kill();
            }
            catch (ArgumentException)
            {
            }
        }

        /// <summary>
        /// Runs the Python process to plot the chosen driver's lap times, via a .bat file
        /// </summary>
        /// <param name="batFileName"> String, the name of the bat file exactly as it appears in the file explorer. </param>
        /// <param name="inputArgList"> List of Strings, containing the user input arguments to be passed to the Python script. </param>
        /// <param name="argMode"> Boolean, if true then parses the arguments like ""arg1,arg2,arg3,..."". Otherwise, parses the arguments like ""arg1" "arg2" "arg3" ...". </param>
        public Process RunPython(string batFileName, List<string> inputArgList, bool argMode=false)
        {
            Process proc = null;
            string batDir = string.Format(@"C:\Users\jamie\OneDrive\Documents\Visual Studio 2019\Projects\F1_Strategy_Interface\bat_files");
            proc = new Process();
            proc.StartInfo.WorkingDirectory = batDir;
            proc.StartInfo.FileName = batFileName;
            proc.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;

            StringBuilder sb = new StringBuilder("");
            if (argMode)
            {
                // Construct a string like ""arg1,arg2,arg3",..."
                sb.Append("\"");
                foreach (string arg in inputArgList)
                {
                    foreach (char c in arg)
                    {
                        sb.Append(c);
                    }
                    sb.Append(",");
                }
                sb.Remove(sb.Length - 1, 1);  // Removes the final trailing comma
                sb.Append("\"");
            }
            else
            {
                // Construct a string like ""arg1" "arg2" "arg3" ..."
                foreach (string arg in inputArgList)
                {
                    sb.Append("\"");
                    foreach (char c in arg)
                    {
                        sb.Append(c);
                    }
                    sb.Append("\"");
                    sb.Append(" ");
                }
            }
            proc.StartInfo.Arguments = sb.ToString();
            return proc;
        }
    }
}
