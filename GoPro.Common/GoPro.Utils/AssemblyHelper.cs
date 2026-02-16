using System;
using System.Collections.Generic;
using System.Reflection;

namespace GoPro.Utils
{
	public class AssemblyHelper
	{
		public enum AssemblyVersionState
		{
			IDENTICAL,
			OLDER,
			NEWER
		}

		public static string Version => GetAssemblyAttribute<AssemblyFileVersionAttribute>().Version;

		public static string Copyright => GetAssemblyAttribute<AssemblyCopyrightAttribute>().Copyright;

		public static int[] ConvertVersionToArray(string version)
		{
			if (string.IsNullOrEmpty(version))
			{
				return new int[3];
			}
			string[] array = version.Split(new char[1] { '.' });
			List<int> list = new List<int>();
			for (int i = 0; i < array.Length; i++)
			{
				if (int.TryParse(array[i], out var result))
				{
					list.Add(result);
				}
			}
			return list.ToArray();
		}

		public static AssemblyVersionState CheckVersionState(string version, int digitCount = int.MaxValue)
		{
			if (Version == version)
			{
				return AssemblyVersionState.IDENTICAL;
			}
			string[] array = Version.Split(new char[1] { '.' });
			digitCount = Math.Min(array.Length, digitCount);
			for (int i = 0; i < digitCount && i < version.Length; i++)
			{
				int num = int.Parse(array[i]);
				int num2 = version[i];
				if (num < num2)
				{
					return AssemblyVersionState.OLDER;
				}
			}
			return AssemblyVersionState.NEWER;
		}

		private static T GetAssemblyAttribute<T>()
		{
			return (T)Assembly.GetEntryAssembly()!.GetCustomAttributes(typeof(T), inherit: false)[0];
		}
	}
}
