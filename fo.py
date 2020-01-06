# -*- coding: utf-8 -*-

'''''''''''''''''''''''''''''''''
@Author : Vic P.
@Email  : vic4key@gmail.com
@Name   : File Operations
'''''''''''''''''''''''''''''''''

import os, sys, argparse, shutil
from PyVutils import File, Others

OPERATIONS = {
	"difference": (set.difference, "+"),
	"intersection": (set.intersection, "="),
	"complement": (lambda s1, s2: s2.difference(s1), "-"),
	"union": (set.union, "*"),
}

ACTIONS = {
	"copy": (shutil.copy, "C"),
	"move": (shutil.move, "M"),
	"delete": (lambda s, _: os.remove(s), "D"),
}

def confirm_action(action):
	while True:
		choice = input(f"\tPerform action `{action}` (yes/no) ? ").lower()
		if choice in ["yes", "y"]: return True
		elif choice in ["no", "n"]: return False
	return False

def get_contained_paths(directory):
	result = []
	len_directory = len(directory)
	if directory[-1] not in [R"/", "\\"]: len_directory += 1
	File.LSRecursive(directory, lambda path, dir, name :
		result.append((path.lower()[len_directory:], dir.lower()[len_directory:], name.lower())))
	return sorted(result)

def main():

	# parse arguments

	parser = argparse.ArgumentParser(description="File Operations")
	parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Print the verbose information")
	parser.add_argument("-c", "--command", type=str, choices=OPERATIONS.keys(), required=True, help="The command")
	parser.add_argument("-p", "--primary_dir", type=str, required=True, help="The primary directory")
	parser.add_argument("-s", "--secondary_dir", type=str, required=True, help="The secondary directory")
	parser.add_argument("-a", "--action", type=str, choices=ACTIONS.keys(), help="The action for the command result")
	parser.add_argument("-d", "--action_dir", type=str, help="The directoty for the action result")
	args = parser.parse_args()

	primary_paths = get_contained_paths(args.primary_dir)
	secondary_paths = get_contained_paths(args.secondary_dir)

	# print primary and secondary file paths

	if args.verbose:
		print("[INFO] List primary paths")
		for e in primary_paths:
			path = os.path.join(args.primary_dir, e[0])
			print(f"\t[FILE] '{path}'")
		print()

		print("[INFO] List secondary paths")
		for e in secondary_paths:
			path = os.path.join(args.secondary_dir, e[0])
			print(f"\t[FILE] '{path}'")
		print()

	primary_paths = set(primary_paths)
	secondary_paths = set(secondary_paths)

	# get operator object by name

	command = args.command.lower()
	fn_operate, sign = OPERATIONS.get(command)

	# perform and print the operation result

	result = fn_operate(primary_paths, secondary_paths)

	if not result:
		print("No result")
		return 0

	result = sorted(list(result))

	print(f"[INFO] The primary / {command}")
	for e in result:
		path = os.path.join(args.primary_dir, e[0])
		print(f"\t[{sign}] '{path}'")
	print()

	# for performing the action

	if args.action:

		# get action object by name

		action = args.action.lower()
		fn_action, sign = ACTIONS.get(action)

		if command in ["complement", "union"]:
			print(f"[ERROR] Unsupported the action `{action}` for the command `{command}`")
			return -1

		# Check the action directory

		is_required_dir = action in ["copy", "move"]

		if is_required_dir and not args.action_dir:
			parser.error("[ERROR] Required the directory for the requested action")
			return -1

		print(f"[INFO] The primary / {action}")

		# confirm to perform the action

		if not confirm_action(action):
			print()
			print(f"[INFO] Canceled the action `{action}`")
			return 0

		# perform the action

		for e in result:

			if is_required_dir:
				dst_dir = os.path.join(args.action_dir, e[1])
				if not File.IsDirectoryExists(dst_dir): os.makedirs(dst_dir)

			src = os.path.join(args.primary_dir, e[0])
			dst = os.path.join(args.action_dir, e[0]) if is_required_dir else ""

			print(f"\t[{sign}] `{src}` => `{dst}`")
			fn_action(src, dst)

		print()

	elif args.action_dir:
		parser.error("[Error] Required the action for requested directory")
		return -1

	print("[INFO] Done")

	return 0

if __name__ == "__main__":
	try: sys.exit(main())
	except (Exception, KeyboardInterrupt): Others.LogException(sys.exc_info())