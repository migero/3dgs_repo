using System;
using System.Reflection;

namespace GoPro.Utils
{
	public static class ObjectExtensions
	{
		private static BindingFlags FLAGS = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

		private static readonly MethodInfo CloneMethod = typeof(object).GetMethod("MemberwiseClone", FLAGS);

		public static T DeepCopy<T>(this T obj)
		{
			return (T)DeepCopyInternal(obj);
		}

		private static object DeepCopyInternal(object obj)
		{
			object obj2 = CloneMethod.Invoke(obj, null);
			FieldInfo[] fields = obj.GetType().GetFields(FLAGS);
			foreach (FieldInfo fieldInfo in fields)
			{
				object value = fieldInfo.GetValue(obj);
				if (value != null)
				{
					if (fieldInfo.FieldType.IsPrimitive || fieldInfo.FieldType == typeof(string))
					{
						fieldInfo.SetValue(obj2, value);
						continue;
					}
					_ = fieldInfo.FieldType;
					object value2 = DeepCopyInternal(value);
					fieldInfo.SetValue(obj2, value2);
				}
			}
			return obj2;
		}

		public static bool DeepEquals(this object objA, object objB)
		{
			return DeepEqualsInternal(objA, objB);
		}

		private static bool DeepEqualsInternal(object objA, object objB)
		{
			if (objB == null)
			{
				return false;
			}
			Type type = objA.GetType();
			Type type2 = objB.GetType();
			if (type != type2)
			{
				return false;
			}
			FieldInfo[] fields = type2.GetFields();
			foreach (FieldInfo fieldInfo in fields)
			{
				object value = fieldInfo.GetValue(objA);
				object value2 = fieldInfo.GetValue(objB);
				if (fieldInfo.FieldType.IsPrimitive || fieldInfo.FieldType.IsEnum)
				{
					if (!value.Equals(value2))
					{
						return false;
					}
				}
				else if (!DeepEqualsInternal(value, value2))
				{
					return false;
				}
			}
			return true;
		}

		public static bool IsDefault<T>(this T obj) where T : new()
		{
			return DeepEqualsInternal(obj, new T());
		}
	}
}
